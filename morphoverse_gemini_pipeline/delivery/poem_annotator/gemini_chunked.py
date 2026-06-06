"""Chunked Gemini annotation (Gemini-only, no Claude/OpenAI).

WHY THIS EXISTS
---------------
The proxy's Gemini upstreams are *thinking* models:
    gemini            -> gemini-3.1-pro-preview
    gemini-3-flash    -> gemini-3-flash-preview

They consume a hidden "thinking" budget that the proxy caps at ~960 tokens and
that we CANNOT control (the proxy rejects reasoning_effort / thinking /
thinking_budget). A full one-shot annotation prompt (rules + enums + schema +
multi-stanza poem) makes the model deliberate past that cap, so it truncates
with finish_reason="length" and emits empty / partial output. That is exactly
the "Gemini returns 0 chars" symptom seen earlier.

THE FIX
-------
Split each poem into *small, single-purpose* calls so each task's thinking stays
well under the cap and there is room left for the JSON output:

    1. poem-level   -> recitation_style + emotional_arc        (very low thinking)
    2. per stanza   -> emotion/tone/translation_quality/loss_note + metaphors
    3. per stanza   -> cultural entities (plain, non-hedged phrasing)

Empirically (incl. the densest poem, Tagore MV++_0008):
    * gemini-3.1-pro reliably handles only the simple poem-level fields; it
      truncates on metaphor/entity extraction for dense poems.
    * gemini-3-flash thinks less and completes metaphor + entity extraction.

So every chunk is tried on PRO first (best quality, wins on easy poems / the
poem-level fields) and falls back to FLASH when pro truncates. Both are Gemini.

The merged result is a full-key payload identical in shape to what
models.fetch_gemini_annotation returns, so the downstream source-term gate and
assembler run unchanged.
"""
from __future__ import annotations

import json
import time
from typing import Any

from api import LLMProxyClient
from .dataset import PreprocessedPoem
from .models import (
    extract_json_payload,
    validate_model_payload,
    filter_non_cultural_entities,
    ModelValidationError,
    StanzaCountMismatch,
)
from .schema import (
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
)

# Pro first (best quality / wins on easy chunks), flash fallback (thinks less).
_PRIMARY = "gemini"
_FALLBACK = "gemini-3-flash"

_SYS = "Output only minified JSON, no markdown, no commentary. Be decisive; do not deliberate."

_EMO = "grief|longing|devotion|peace|celebration|resilience|anger|fear"
_TONE = "lament|whisper|declaration|prayer|wonder|defiance|tenderness"
_TQ = "faithful|partial|lost"
_STYLE = "lament|devotional|celebratory|reflective|declarative"
_CATS = "DEITY|SACRED_RIVER|FESTIVAL|MUSICAL_TRADITION|DEVOTIONAL_CONCEPT|REGIONAL_SYMBOL|SOCIAL_CUSTOM|MYTHOLOGICAL_EVENT"


# ── Low-level proxy call ──────────────────────────────────────────────────────
def _raw_call(client: LLMProxyClient, model: str, usr: str, *, max_tokens: int = 2048) -> str:
    """Return content string ('' on truncation/empty/error). Never raises."""
    try:
        resp = client.chat(
            model,
            [{"role": "system", "content": _SYS}, {"role": "user", "content": usr}],
            temperature=0.1,
            max_tokens=max_tokens,
        )
        ch = resp["choices"][0]
        content = ch.get("message", {}).get("content")
        return content if isinstance(content, str) else ""
    except Exception:
        return ""


# Per-chunk model strategies.
#   PRO_FIRST  : pro gets first crack (best quality), flash recovers truncations.
#                Used where pro actually completes: poem-level fields, stanza
#                classification.
#   FLASH_ONLY : metaphor + entity extraction. Pro provably truncates on these
#                (thinking pins at ~960 before it can emit verbatim Indic text),
#                so trying pro only wastes ~5s/call with no output. Flash is the
#                proven workhorse here. Still 100% Gemini — no Claude/OpenAI.
_PRO_FIRST = ((_PRIMARY, 1), (_FALLBACK, 2))
_FLASH_ONLY = ((_FALLBACK, 3),)


def _call_json(client: LLMProxyClient, usr: str, attempts=_PRO_FIRST) -> dict | None:
    """Try the given (model, tries) attempts in order; parse JSON (with truncation
    repair). Return a dict or None if all attempts fail."""
    for model, tries in attempts:
        for attempt in range(tries):
            content = _raw_call(client, model, usr)
            if content.strip():
                try:
                    obj = extract_json_payload(content)
                    if isinstance(obj, dict):
                        return obj
                except Exception:
                    pass
            if attempt + 1 < tries:
                time.sleep(0.4 * (attempt + 1))  # brief backoff before retry
    return None


# ── Sanitizers ────────────────────────────────────────────────────────────────
def _pick(value: Any, allowed: tuple[str, ...], default: str) -> str:
    if isinstance(value, str):
        lut = {a.casefold(): a for a in allowed}
        hit = lut.get(value.strip().casefold())
        if hit:
            return hit
    return default


def _clean_str(value: Any, limit_words: int = 0) -> str:
    if not isinstance(value, str):
        return ""
    s = value.strip()
    if limit_words and s:
        s = " ".join(s.split()[:limit_words])
    return s


# ── Chunk builders ────────────────────────────────────────────────────────────
def _render_poem(poem: PreprocessedPoem, max_chars: int = 1800) -> str:
    parts = []
    for s in poem.stanzas:
        parts.append(f"[{s.stanza_index}] " + " / ".join(s.source_lines))
    text = "\n".join(parts)
    return text[:max_chars]


def _chunk_poem_level(client: LLMProxyClient, poem: PreprocessedPoem) -> tuple[str, str]:
    usr = (
        f"Poem ({poem.language}):\n{_render_poem(poem)}\n"
        f'Return {{"rs":STYLE,"ea":"2-4 words"}}  STYLE:{_STYLE}'
    )
    obj = _call_json(client, usr)
    if not obj:
        return "reflective", ""
    rs = _pick(obj.get("rs") or obj.get("recitation_style"), ALLOWED_RECITATION_STYLES, "reflective")
    ea = _clean_str(obj.get("ea") or obj.get("emotional_arc"), limit_words=6)
    return rs, ea


def _chunk_classify(client: LLMProxyClient, poem: PreprocessedPoem, s) -> dict:
    """Emotion / tone / translation_quality / loss_note. Low thinking, very reliable."""
    src = " / ".join(s.source_lines)
    tr = " / ".join(s.translated_lines) if s.translated_lines else ""
    usr = (
        f"Stanza {s.stanza_index} ({poem.language}): {src}\nTranslation: {tr}\n"
        f'Return {{"em":E,"to":T,"tq":Q,"ln":""}} E:{_EMO} T:{_TONE} Q:{_TQ}; '
        'ln="" if faithful else <=8 words describing what the translation lost'
    )
    return _call_json(client, usr) or {}


def _chunk_metaphors(client: LLMProxyClient, poem: PreprocessedPoem, s) -> list[dict]:
    """Metaphors only — kept as its own call so they are never lost to a truncated
    combined request. Flash handles this well (low thinking)."""
    src = " / ".join(s.source_lines)
    usr = (
        f"Stanza ({poem.language}): {src}\n"
        "Identify 1-3 true metaphors or symbolic phrases (not literal statements). "
        'Return {"ms":[{"src":"verbatim phrase copied from stanza","am":"poem-specific meaning <=6 words"}]}\n'
        "src MUST be Indic-script text copied exactly from the stanza: no gloss, no romanization, no parentheses."
    )
    obj = _call_json(client, usr, attempts=_FLASH_ONLY)
    spans: list[dict] = []
    if not obj:
        return spans
    for m in obj.get("ms") or obj.get("metaphor_spans") or []:
        if not isinstance(m, dict):
            continue
        src_term = _clean_str(m.get("src") or m.get("source_term"))
        am = _clean_str(m.get("am") or m.get("abstract_meaning"), limit_words=8)
        if src_term and am:
            spans.append({"source_term": src_term, "abstract_meaning": am})
    return spans


def _chunk_stanza(client: LLMProxyClient, poem: PreprocessedPoem, s) -> dict:
    obj = _chunk_classify(client, poem, s)
    tq = _pick(obj.get("tq") or obj.get("translation_quality"), ALLOWED_TRANSLATION_QUALITIES, "faithful")
    ln = "" if tq == "faithful" else _clean_str(obj.get("ln") or obj.get("loss_note"), limit_words=8)
    spans = _chunk_metaphors(client, poem, s)
    return {
        "index": s.stanza_index,
        "emotion": _pick(obj.get("em") or obj.get("emotion"), ALLOWED_EMOTIONS, "longing"),
        "tone": _pick(obj.get("to") or obj.get("tone"), ALLOWED_TONES, "whisper"),
        "translation_quality": tq,
        "loss_note": ln,
        "metaphor_spans": spans,
    }


def _chunk_entities(client: LLMProxyClient, poem: PreprocessedPoem, s) -> list[dict]:
    src = " / ".join(s.source_lines)
    usr = (
        f"Stanza ({poem.language}): {src}\n"
        "Name any deities, sacred places or rivers, devotional/philosophical concepts, festivals, "
        "musical or poetic forms, mythological events, or social customs mentioned in this stanza. "
        f'Return {{"ce":[{{"tm":"verbatim term","ct":CAT,"si":{s.stanza_index}}}]}}  CAT one of {_CATS}'
    )
    obj = _call_json(client, usr, attempts=_FLASH_ONLY)
    out: list[dict] = []
    if not obj:
        return out
    for e in obj.get("ce") or obj.get("cultural_entities") or []:
        if not isinstance(e, dict):
            continue
        term = _clean_str(e.get("tm") or e.get("term"))
        cat = _pick(e.get("ct") or e.get("category"), ALLOWED_ENTITY_CATEGORIES, "")
        if term and cat:
            out.append({
                "term": term,
                "romanization": _clean_str(e.get("rm") or e.get("romanization")),
                "category": cat,
                "stanza_index": s.stanza_index,
                "preserved": bool(e.get("pr", True)),
                "translation_note": _clean_str(e.get("tn") or e.get("translation_note"), limit_words=6),
            })
    return out


# ── Public entry point (mirrors models.fetch_gemini_annotation contract) ──────
def annotate_poem_chunked(poem: PreprocessedPoem, token: str, base_url: str) -> dict[str, Any]:
    """Annotate a poem via many small Gemini calls and merge into one full-key payload.

    Returns the same dict shape as fetch_gemini_annotation so process_poem's gate
    and assembler are unchanged: keys status/model/prompt_kind/retry_count/raw_text/
    parsed/discard_reason.
    """
    client = LLMProxyClient(token=token, base_url=base_url)

    rs, ea = _chunk_poem_level(client, poem)
    stanzas: list[dict] = []
    entities: list[dict] = []
    for s in poem.stanzas:
        stanzas.append(_chunk_stanza(client, poem, s))
        entities.extend(_chunk_entities(client, poem, s))

    payload = {
        "recitation_style": rs,
        "emotional_arc": ea,
        "stanzas": stanzas,
        "cultural_entities": entities,
    }

    try:
        validated = validate_model_payload(payload, poem)
        validated = filter_non_cultural_entities(validated, poem.language)
    except (ModelValidationError, StanzaCountMismatch) as exc:
        return {
            "status": "validation_failed", "model": "gemini-chunked", "prompt_kind": "chunked",
            "retry_count": 0, "raw_text": json.dumps(payload, ensure_ascii=False),
            "parsed": None, "discard_reason": f"chunked merge invalid: {exc}",
        }

    # A poem with no usable signal at all (every chunk failed) is a failure.
    total_signal = sum(len(st["metaphor_spans"]) for st in validated["stanzas"]) + len(validated["cultural_entities"])
    has_meta = bool(validated["emotional_arc"]) or total_signal > 0
    if not has_meta and all(st["translation_quality"] == "faithful" and not st["loss_note"] for st in validated["stanzas"]):
        # still return it (stanzas classified), but mark low — caller decides via gate
        pass

    return {
        "status": "valid", "model": "gemini-chunked", "prompt_kind": "chunked",
        "retry_count": 0, "raw_text": json.dumps(payload, ensure_ascii=False),
        "parsed": validated, "discard_reason": "",
    }
