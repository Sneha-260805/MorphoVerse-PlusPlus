"""Shared, language-agnostic prompt builder (Gemini-only, abbreviated JSON output).

TOKEN-BUDGET FIX (proxy completion cap ~37 tokens / ~160 chars):
  The proxy caps completion at ~37 tokens regardless of max_tokens (768-1536).
  A full-key 1-stanza annotation JSON is ~202 chars (>37 tokens) — always truncated.

  Fix: request abbreviated output keys so the model's response fits within the cap.
    Full: {"recitation_style":...,"stanzas":[{"index":1,"emotion":...}]} = 202+ chars
    Abbr: {"rs":...,"st":[{"i":1,"em":...}]}                             = 107 chars ✓

  The pipeline calls expand_abbreviated_keys() before validation so downstream
  code sees full field names and does not need to change.

  Examples are omitted from the primary prompt to reduce input tokens (~800 → ~250),
  which gives the proxy slightly more output budget and avoids Indic-script token bloat.
"""
from __future__ import annotations

import json
import re

from .dataset import PreprocessedPoem
from .schema import (
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a multilingual poem annotation engine specializing in Indian language poetry. "
    "Indian poetry is culturally rich — expect 2-8 cultural entities per poem and 1-3 metaphors per stanza. "
    "Annotate ALL culture-bearing terms: deities, devotional concepts, place names, historical figures, epics, literary forms. "
    "Return exactly one minified abbreviated JSON object using the compact key names shown. "
    "No markdown, no commentary, no extra keys, no explanation."
)

# ── Abbreviated format reference (shown inline in every prompt) ───────────────
_ABBREV_FORMAT = (
    '{"rs":"STYLE","ea":"3-4 words",'
    '"st":[{"i":1,"em":"EMOTION","to":"TONE","tq":"QUALITY","ln":"5 words max",'
    '"ms":[{"src":"SOURCE_PHRASE","am":"6 words max"}]}],'
    '"ce":[{"tm":"INDIC_TERM","rm":"ROMAN","ct":"CATEGORY","si":1,"pr":true,"tn":"4 words max"}]}'
)
_ABBREV_KEYS = (
    "rs=recitation_style  ea=emotional_arc(MAX 4 WORDS)  st=stanzas  ce=cultural_entities  "
    "i=index  em=emotion  to=tone  tq=translation_quality  ln=loss_note(MAX 5 WORDS ASCII)  "
    "ms=metaphor_spans(src=source_term verbatim Indic script, am=abstract_meaning MAX 6 WORDS)  "
    "tm=term  rm=romanization  ct=category  si=stanza_index  pr=preserved  tn=translation_note(MAX 4 WORDS ASCII)"
)
_ABBREV_ENTITY_FORMAT = (
    '{"tm":"INDIC_TERM","rm":"ROMAN","ct":"CATEGORY","si":STANZA_INT,"pr":BOOL,"tn":"NOTE_8WORDS_MAX"}'
)
_ABBREV_ENTITY_KEYS = "tm=term  rm=romanization  ct=category  si=stanza_index  pr=preserved  tn=translation_note"

# ── Rules ─────────────────────────────────────────────────────────────────────
_RULES_TEMPLATE = """\
RULES:
1. Exactly {n} stanza object(s) in st[], indexed 1..{n}.
2. ms: identify true metaphors/symbols with poem-specific meaning; aim for 1-3 per stanza. st MUST be verbatim Indic-script text copied exactly from SOURCE — NO English gloss, NO romanization, NO parentheses added. am MUST be 6 words max English ASCII. Use [] only for purely factual stanzas with no figurative language.
3. tm (entity term) MUST be a verbatim substring of the SOURCE text shown. rm = English romanization.
4. ln MUST be "" when tq="faithful". When tq is partial/lost, ln MUST be 5 words max English ASCII. NEVER write a full sentence.
5. tn MUST be 4 words max English ASCII. NEVER write a full sentence.
6. ce MUST include ALL culture-bearing terms from SOURCE: DEITY (named gods/goddesses), DEVOTIONAL_CONCEPT (karma, moksha, dharma, ishq, fana, bhakti, maya, viraha, rasa), REGIONAL_SYMBOL (place names, national/cultural symbols), SACRED_RIVER (Ganga, Godavari, Yamuna), FESTIVAL (Diwali, Eid, Puja), MUSICAL_TRADITION (ghazal, doha, kirtan, abhanga, raga), MYTHOLOGICAL_EVENT (epics, Ramayana, Mahabharata, Karbala), SOCIAL_CUSTOM (purdah, sati, mehfil). Expect 2-8 entities per poem. Generic words (sky, river, moon, flower) without cultural weight are NOT entities.
7. ea MUST be 4 words max English ASCII (e.g. "grief to peace", "longing through joy"). NEVER write a sentence."""

# ── Main user prompt template ─────────────────────────────────────────────────
_USER_TEMPLATE = """\
LANGUAGE: {language} | STANZAS: {n}{hints_line}

{stanza_render}

ALLOWED:
rs: {recitation_styles}
em: {emotions}
to: {tones}
tq: {translation_qualities}
ct: {entity_categories}

{rules}

OUTPUT FORMAT (abbreviated keys only):
{abbrev_format}
{abbrev_keys}
entity item: {abbrev_entity_fmt}  |  {abbrev_entity_keys}

Return the minified abbreviated JSON now."""

# ── Repair prompt ─────────────────────────────────────────────────────────────
_REPAIR_TEMPLATE = """\
Your previous response was not valid JSON. Return ONLY one minified abbreviated JSON.
Required: rs/ea/st/ce at top level. Exactly {n} stanza(s) in st[] indexed 1..{n}.
Each stanza: i em to tq ln ms. ln="" when tq=faithful; otherwise max 6 words ASCII. tm/src verbatim from SOURCE.

{stanza_render}

ALLOWED: rs={recitation_styles} em={emotions} to={tones} tq={translation_qualities} ct={entity_categories}
FORMAT: {abbrev_format}
Return now."""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _render_stanzas(poem: PreprocessedPoem) -> str:
    parts = []
    for s in poem.stanzas:
        src = " | ".join(s.source_lines)
        tr = " | ".join(s.translated_lines) if s.translated_lines else "[no translation]"
        parts.append(f"[STANZA {s.stanza_index}]\nSOURCE: {src}\nTRANSLATION: {tr}")
    return "\n\n".join(parts)


def _format_hints(ctx: dict) -> str:
    if not ctx:
        return ""
    parts: list[str] = []
    arc = ctx.get("suggested_emotional_arc") or ""
    if arc and arc != "unknown":
        parts.append(f"emotion_hint={arc}")
    terms = ctx.get("likely_cultural_terms") or []
    if terms:
        short = [f"{t['term']}({t['category']})" for t in terms[:3] if t.get("term")]
        if short:
            parts.append(f"cultural_hints={','.join(short)}")
    align = ctx.get("translation_alignment_score")
    if align is not None:
        parts.append(f"alignment={align:.2f}")
    return f" | ADVISORY({'; '.join(parts)})" if parts else ""


def _format_examples(examples: list[dict], cap: int = 2) -> str:
    """Render at most `cap` examples as abbreviated JSON for schema reference.

    Only the output JSON is shown (abbreviated form). Input stanza context is
    omitted to keep input tokens low. The model sees the format from _USER_TEMPLATE.
    """
    if not examples:
        return ""
    parts: list[str] = []
    for i, ex in enumerate(examples[:cap], 1):
        out = ex.get("output", {})
        if not isinstance(out, str):
            out_dict = out
        else:
            try:
                out_dict = json.loads(out)
            except Exception:
                continue
        # Convert full-key example output to abbreviated form for compact display
        abbrev_out = _to_abbreviated(out_dict)
        parts.append(f"EX{i}: {json.dumps(abbrev_out, ensure_ascii=False, separators=(',', ':'))}")
    return ("EXAMPLE OUTPUTS (abbreviated schema reference):\n" + "\n".join(parts)) if parts else ""


def _to_abbreviated(full_dict: dict) -> dict:
    """Convert a full-key annotation dict to abbreviated keys for display in examples."""
    if not isinstance(full_dict, dict):
        return full_dict
    from .schema import ABBREV_TOPLEVEL, ABBREV_STANZA, ABBREV_METAPHOR, ABBREV_ENTITY
    inv_top = {v: k for k, v in ABBREV_TOPLEVEL.items()}
    inv_st  = {v: k for k, v in ABBREV_STANZA.items()}
    inv_ms  = {v: k for k, v in ABBREV_METAPHOR.items()}
    inv_ent = {v: k for k, v in ABBREV_ENTITY.items()}

    result = {inv_top.get(k, k): v for k, v in full_dict.items()}
    if "st" in result and isinstance(result["st"], list):
        new_st = []
        for st in result["st"]:
            if not isinstance(st, dict):
                new_st.append(st)
                continue
            exp = {inv_st.get(k, k): v for k, v in st.items()}
            if "ms" in exp and isinstance(exp["ms"], list):
                exp["ms"] = [{inv_ms.get(k, k): v for k, v in m.items()}
                             if isinstance(m, dict) else m for m in exp["ms"]]
            new_st.append(exp)
        result["st"] = new_st
    if "ce" in result and isinstance(result["ce"], list):
        result["ce"] = [{inv_ent.get(k, k): v for k, v in e.items()}
                        if isinstance(e, dict) else e for e in result["ce"]]
    return result


def _enums(sep: str = " | ") -> dict:
    return dict(
        recitation_styles=sep.join(ALLOWED_RECITATION_STYLES),
        emotions=sep.join(ALLOWED_EMOTIONS),
        tones=sep.join(ALLOWED_TONES),
        translation_qualities=sep.join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories=sep.join(ALLOWED_ENTITY_CATEGORIES),
    )


# ── Public API ────────────────────────────────────────────────────────────────
def build_prompt_bundle(
    poem: PreprocessedPoem,
    examples: list[dict],
    language_note: str = "",
    semantic_context: dict | None = None,
) -> tuple[str, str, str]:
    """Return (system_prompt, user_prompt, repair_prompt).

    examples are optionally appended as abbreviated schema reference after the
    format block. language_note is prepended to hints if non-empty.
    """
    n = len(poem.stanzas)
    stanza_render = _render_stanzas(poem)
    enums = _enums()
    enums_flat = _enums(sep="|")

    hints_line = _format_hints(semantic_context or {})
    if language_note:
        note_str = f" | NOTE: {language_note}"
        hints_line = note_str + hints_line

    # Skip examples from the primary prompt: they contain Indic script in loss_notes
    # which tokenize expensively and inflate input tokens beyond the proxy's budget.
    # The abbreviated format template is self-contained.

    user = _USER_TEMPLATE.format(
        language=poem.language,
        n=n,
        hints_line=hints_line,
        stanza_render=stanza_render,
        rules=_RULES_TEMPLATE.format(n=n),
        abbrev_format=_ABBREV_FORMAT,
        abbrev_keys=_ABBREV_KEYS,
        abbrev_entity_fmt=_ABBREV_ENTITY_FORMAT,
        abbrev_entity_keys=_ABBREV_ENTITY_KEYS,
        **enums,
    )

    repair = _REPAIR_TEMPLATE.format(
        n=n,
        stanza_render=stanza_render,
        abbrev_format=_ABBREV_FORMAT,
        **enums_flat,
    )

    return SYSTEM_PROMPT, user, repair
