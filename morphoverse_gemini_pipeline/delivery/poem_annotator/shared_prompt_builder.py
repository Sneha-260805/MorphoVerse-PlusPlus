"""Shared, language-agnostic prompt builder (Gemini-only, neutral, one schema).

Language files supply ONLY data: an EXAMPLES list and an optional LANGUAGE_NOTE.
Neutral, evidence-bound; one canonical schema.
"""
from __future__ import annotations

import json

from .dataset import PreprocessedPoem
from .schema import (
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
)

SYSTEM_PROMPT = (
    "Annotate only what is supported by the source poem and translation. "
    "Do not infer cultural entities, metaphors, emotions, or symbolism that are not "
    "directly present in the text. When evidence is weak or ambiguous, choose the most "
    "conservative label and leave optional arrays empty. "
    "Every cultural_entities.term and metaphor_spans.source_term MUST be copied verbatim "
    "from the source text. "
    "Return exactly one valid minified JSON object using the schema and enums provided. "
    "No markdown, no commentary, no extra fields."
)

RULES = """\
RULES:
1. Return one minified JSON object. No markdown, no prose outside JSON.
2. Use exactly the allowed labels for recitation_style, emotion, tone, translation_quality, category.
3. Top-level keys exactly: recitation_style, emotional_arc, stanzas, cultural_entities. No other fields.
4. Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
5. Stanza keys exactly: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
6. If translation_quality is faithful, loss_note must be "".
7. cultural_entities.term and metaphor_spans.source_term MUST be copied verbatim from the SOURCE text.
8. Do not tag generic nature/body/season words as cultural entities.
9. Use [] for metaphor_spans / cultural_entities when none are clearly supported.
10. Named deities explicitly present in the source MUST be tagged DEITY.
"""

USER_TEMPLATE = """\
LANGUAGE: {language}
STANZA_COUNT: {stanza_count}
{language_note}
STANZAS:
{stanza_render}

ALLOWED:
recitation_style = {recitation_styles}
emotion = {emotions}
tone = {tones}
translation_quality = {translation_qualities}
category = {entity_categories}

{rules}

EXAMPLES:
{examples}

Return the JSON object now.
"""

REPAIR_TEMPLATE = """\
Your previous answer was invalid. Return only one minified JSON object.
Top-level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
Stanza keys: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
Forbidden: any key not listed above, markdown, commentary.
Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
If translation_quality is faithful then loss_note="".
Every term/source_term must be copied verbatim from SOURCE.
STANZAS:
{stanza_render}
ALLOWED: recitation_style={recitation_styles}; emotion={emotions}; tone={tones}; \
translation_quality={translation_qualities}; category={entity_categories}
"""


def _render_stanzas(poem: PreprocessedPoem) -> str:
    out = []
    for s in poem.stanzas:
        src = " | ".join(s.source_lines)
        tr = " | ".join(s.translated_lines) if s.translated_lines else "[NO TRANSLATED LINES]"
        out.append(f"[STANZA {s.stanza_index}]\nSOURCE: {src}\nTRANSLATION: {tr}")
    return "\n\n".join(out)


def _format_examples(examples: list[dict]) -> str:
    parts = []
    for i, ex in enumerate(examples, 1):
        out = ex["output"]
        if not isinstance(out, str):
            out = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
        parts.append(f"EXAMPLE {i}:\nINPUT:\n{ex['input']}\nOUTPUT:\n{out}")
    return "\n\n".join(parts) if parts else "(no examples available for this language)"


def _enums(sep: str) -> dict[str, str]:
    return dict(
        recitation_styles=sep.join(ALLOWED_RECITATION_STYLES),
        emotions=sep.join(ALLOWED_EMOTIONS),
        tones=sep.join(ALLOWED_TONES),
        translation_qualities=sep.join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories=sep.join(ALLOWED_ENTITY_CATEGORIES),
    )


def build_prompt_bundle(poem: PreprocessedPoem, examples: list[dict],
                        language_note: str = "") -> tuple[str, str, str]:
    n = len(poem.stanzas)
    stanza_render = _render_stanzas(poem)
    user = USER_TEMPLATE.format(
        language=poem.language,
        stanza_count=n,
        language_note=(f"NOTE: {language_note}" if language_note else ""),
        stanza_render=stanza_render,
        rules=RULES.format(stanza_count=n),
        examples=_format_examples(examples),
        **_enums(" | "),
    )
    repair = REPAIR_TEMPLATE.format(stanza_count=n, stanza_render=stanza_render, **_enums("|"))
    return SYSTEM_PROMPT, user, repair
