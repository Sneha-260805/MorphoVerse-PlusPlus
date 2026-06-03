from __future__ import annotations

import json

from .config import (
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
)
from .dataset import PreprocessedPoem, StanzaInput

GOLD_SYSTEM_PREFIX = (
    "You are a gold‑standard annotator for MorphoVerse++, a dataset of morphologically rich Indian language poems. "
    "Your annotations must be precise, conservative, text‑grounded, stanza‑aware, and suitable for human academic review. "
    "Do not guess. Do not hallucinate culture. Do not inflate metaphor density. Do not use generic metaphor meanings. "
    "Use the English translation for support, but keep the original‑language cultural meaning as the source of truth. "
)

# Keep the original system prompts for the five languages
SYSTEM_PROMPTS = {
    "Assamese": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Assamese context carefully, including Vaishnavite/Borgeet influence, Brahmaputra imagery, Bihu/seasonal rhythms, Sattriya/Kamakhya only when text-supported. "
        "THIS IS ASSAMESE, NOT BENGALI. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
    "Bengali": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Bengali context carefully, including Tagore/Baul/Padma/Shravan/Durga/partition resonance only when text-supported. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
    "Hindi": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Hindi/Sanskrit-rooted devotional context carefully, including Ramayana, Mahabharata, Bhakti, dharma, vanavas, moksha only when text-supported. "
        "Named deities such as Ram, Krishna, Sita, Madhava, Vishnu MUST be tagged as DEITY. "
        "THIS IS HINDI. DO NOT CONFUSE WITH URDU OR BENGALI. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
    "Marathi": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Marathi context carefully, including Varkari, Tukaram/Dnyaneshwar, Vitthal/Wari, Konkan/Sahyadri, and social terms like Nakoshi only when text-supported. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
    "Telugu": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Telugu context carefully, including Bhakti, Carnatic/prabandha imagery, Venkateshwara, Godavari, veena, koel, jasmine only when text-supported. "
        "Named deities such as Madhava, Krishna, Rama, Venkateshwara must not be dropped when explicitly present. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
}

# For languages not in the original five, use a neutral prompt
_DEFAULT_SYSTEM = GOLD_SYSTEM_PREFIX + (
    "Language hint: this poem is written in a specific Indian language. Annotate strictly from the text. "
    "Return one valid JSON object only. No explanation, no markdown."
)

# Extend the dictionary for all other supported languages
for _lang in {"Bodo", "Dogri", "Gujarati", "Kashmiri", "Punjabi", "Tamil", "Urdu"}:
    SYSTEM_PROMPTS.setdefault(_lang, _DEFAULT_SYSTEM)

COMMON_RULES = """\
RULES:
1. Return JSON only. No markdown, no prose outside JSON.
2. Use exactly the allowed labels for recitation_style, emotion, tone, translation_quality, and category.
3. Do not add extra fields and do not output scene.
4. Use exactly {stanza_count} stanza objects and keep indices 1..{stanza_count}.
5. If translation_quality is faithful, loss_note must be "".
6. loss_note and translation_note must be short, specific, and text‑grounded.
7. cultural_entities must include only explicit or strongly implied culture‑bearing terms.
8. Named deities explicitly present in source text MUST be included as DEITY, even if translation uses a simpler name.
9. Do not treat generic nature/body/season words as cultural entities unless the poem makes them culturally specific.
10. Relational deity epithets such as "Janaka's son‑in‑law" should be DEITY if they refer to the divine figure; use MYTHOLOGICAL_EVENT only when annotating an event itself.
11. metaphor_spans must include only true metaphors/symbolic phrases, not every poetic noun.
12. Metaphor abstract_meaning must be poem‑specific; never use generic filler like "heart = emotion" or "river = life".
13. Use [] for metaphor_spans when none are clearly supported.
14. Visual motifs are NOT required; do NOT output any visual_motifs field.
"""

USER_TEMPLATE = """\
POEM_ID: {poem_id}
POEM_TITLE: {poem_title}
LANGUAGE: {language}
STANZA_COUNT: {stanza_count}
SEMANTIC_PRECOMPUTED_HINTS: {semantic_context}

STANZAS:
{stanza_render}

SCHEMA:
{{
  "recitation_style": "<{recitation_styles}>",
  "emotional_arc": "<short free text>",
  "stanzas": [
    {{
      "index": <1‑based int>,
      "emotion": "<{emotions}>",
      "tone": "<{tones}>",
      "translation_quality": "<{translation_qualities}>",
      "loss_note": "<empty string or one short sentence>",
      "metaphor_spans": [
        {{
          "source_term": "<original script word or phrase>",
          "abstract_meaning": "<one short poem‑specific English phrase>"
        }}
      ]
    }}
  ],
  "cultural_entities": [
    {{
      "term": "<original script>",
      "romanization": "<short romanization or empty string>",
      "category": "<{entity_categories}>",
      "stanza_index": <1‑based int>,
      "preserved": <true|false>,
      "translation_note": "<empty string or one short sentence>"
    }}
  ]
}}

{common_rules}

EXAMPLES:
{example_inputs_and_outputs}
"""

REPAIR_USER_TEMPLATE = """\
Your previous answer was invalid. Return only minified valid JSON using the exact schema below.
No markdown. No extra fields. No scene. No visual_motifs.

Top‑level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
Stanza keys: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
Each metaphor_spans item: source_term, abstract_meaning.
Each cultural_entities item: term, romanization, category, stanza_index, preserved, translation_note.

Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
If translation_quality=faithful then loss_note="".

POEM_ID: {poem_id}
LANGUAGE: {language}
STANZA_COUNT: {stanza_count}
STANZAS:
{stanza_render}

ALLOWED:
recitation_style={recitation_styles}
emotion={emotions}
tone={tones}
translation_quality={translation_qualities}
category={entity_categories}\
"""

GEMINI_SYSTEM_PROMPT = GOLD_SYSTEM_PREFIX + (
    "Return one valid JSON object only. Use the exact schema and enums. No markdown."
)

GEMINI_USER_TEMPLATE = """\
Return one minified JSON object with top‑level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
Each stanza object must have: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
Do NOT include visual_motifs.
Each metaphor_spans item must have: source_term, abstract_meaning.
Each cultural_entities object must have: term, romanization, category, stanza_index, preserved, translation_note.

Rules:
‑ Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
‑ If translation_quality is faithful then loss_note="".
‑ metaphor_spans must be an array; use [] if none.
‑ Include named deities explicitly present in source text as DEITY.
‑ Do not return poem_id, language, stanza_count, source, translation, annotations, scene, or markdown.
‑ Use only these enums:
  recitation_style={recitation_styles}
  emotion={emotions}
  tone={tones}
  translation_quality={translation_qualities}
  category={entity_categories}

Input JSON:
{input_json}\
"""

GEMINI_REPAIR_USER_TEMPLATE = """\
Your previous answer was invalid. Return only minified JSON.
Top‑level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
Stanza keys: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
Metaphor keys: source_term, abstract_meaning.
Entity keys: term, romanization, category, stanza_index, preserved, translation_note.
Forbidden keys: poem_id, language, stanza_count, source, translation, annotations, scene, markdown, visual_motifs.
Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
If translation_quality=faithful then loss_note="".
Allowed enums:
recitation_style={recitation_styles}
emotion={emotions}
tone={tones}
translation_quality={translation_qualities}
category={entity_categories}

Input JSON:
{input_json}\
"""

# ── Render helpers (unchanged) ─────────────────────────────────────────────
def format_stanza_markers(stanzas: list[StanzaInput], field_name: str = "source") -> str:
    rendered: list[str] = []
    for stanza in stanzas:
        lines = stanza.source_lines if field_name == "source" else stanza.translated_lines
        body = "\n".join(lines) if lines else "[NO TRANSLATED LINES AVAILABLE]"
        rendered.append(f"[STANZA {stanza.stanza_index}]\n{body}")
    return "\n\n".join(rendered)


def render_stanzas_for_prompt(poem: PreprocessedPoem) -> str:
    rendered: list[str] = []
    for stanza in poem.stanzas:
        source = " | ".join(stanza.source_lines)
        translated = " | ".join(stanza.translated_lines) if stanza.translated_lines else "[NO TRANSLATED LINES AVAILABLE]"
        rendered.append(
            f"[STANZA {stanza.stanza_index}]\n"
            f"SOURCE: {source}\n"
            f"TRANSLATION: {translated}"
        )
    return "\n\n".join(rendered)


def render_prompt_input_json(poem: PreprocessedPoem) -> str:
    payload = {
        "poem_title": poem.poem_title,
        "language": poem.language,
        "stanza_count": len(poem.stanzas),
        "stanzas": [
            {
                "index": stanza.stanza_index,
                "source": " | ".join(stanza.source_lines),
                "translation": " | ".join(stanza.translated_lines),
            }
            for stanza in poem.stanzas
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

# ── Few‑shot examples (original five languages) ─────────────────────────────
COMPACT_EXAMPLES = {
    "Assamese": {
        "input": "[STANZA 1]\nSOURCE: প্ৰতিমা, তুমি এক নিবেদনে\nTRANSLATION: Idol, you come in a dedication",
        "output": '{"recitation_style":"devotional","emotional_arc":"longing","stanzas":[{"index":1,"emotion":"longing","tone":"prayer","translation_quality":"partial","loss_note":"Pratima loses consecrated devotional nuance.","metaphor_spans":[]}],"cultural_entities":[{"term":"প্রতিমা","romanization":"Pratima","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":false,"translation_note":"Rendered as generic idol."}]}',
    },
    "Bengali": {
        "input": "[STANZA 1]\nSOURCE: ও আমার দেশের মাটি,\nTRANSLATION: O soil of my country,",
        "output": '{"recitation_style":"declarative","emotional_arc":"longing","stanzas":[{"index":1,"emotion":"longing","tone":"declaration","translation_quality":"faithful","loss_note":"","metaphor_spans":[{"source_term":"দেশের মাটি","abstract_meaning":"homeland as intimate source of belonging"}],"visual_motifs":[]}],"cultural_entities":[]}',
    },
    "Hindi": {
        "input": "[STANZA 1]\nSOURCE: वनवास का दर्द सहा था एक बार,\nTRANSLATION: Once the pain of exile was endured,",
        "output": '{"recitation_style":"lament","emotional_arc":"grief","stanzas":[{"index":1,"emotion":"grief","tone":"lament","translation_quality":"partial","loss_note":"Vanavas loses Ramayana-specific sacred exile weight.","metaphor_spans":[]}],"cultural_entities":[{"term":"वनवास","romanization":"vanavas","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":false,"translation_note":"Generic exile loses sacred narrative weight."}]}',
    },
    "Marathi": {
        "input": "[STANZA 1]\nSOURCE: नकोशी जन्मली,\nTRANSLATION: Born unwanted,",
        "output": '{"recitation_style":"declarative","emotional_arc":"grief","stanzas":[{"index":1,"emotion":"grief","tone":"lament","translation_quality":"lost","loss_note":"Nakoshi social meaning disappears.","metaphor_spans":[]}],"cultural_entities":[{"term":"नकोशी","romanization":"Nakoshi","category":"SOCIAL_CUSTOM","stanza_index":1,"preserved":false,"translation_note":"The social practice is omitted."}]}',
    },
    "Telugu": {
        "input": "[STANZA 1]\nSOURCE: పూవై రాలిన తారకవో\nTRANSLATION: A star that withered like a flower,",
        "output": '{"recitation_style":"devotional","emotional_arc":"longing","stanzas":[{"index":1,"emotion":"longing","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[{"source_term":"పూవై రాలిన తారకవో","abstract_meaning":"beloved imagined as a fallen star-flower"}]}],"cultural_entities":[]}',
    },
}

def format_examples(language):
    ex = COMPACT_EXAMPLES.get(language)
    if ex is None:
        # return a minimal valid example
        return "EXAMPLE:\nINPUT:\n[STANZA 1]\nSOURCE: generic line\nTRANSLATION: generic line\nOUTPUT:\n" + json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "unknown",
            "stanzas": [{"index":1,"emotion":"peace","tone":"tenderness","translation_quality":"faithful","loss_note":"","metaphor_spans":[]}],
            "cultural_entities": []
        }, ensure_ascii=False)
    return f"EXAMPLE:\nINPUT:\n{ex['input']}\nOUTPUT:\n{ex['output']}\n"


# ── Prompt builders ─────────────────────────────────────────────────────────
def build_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    system = SYSTEM_PROMPTS.get(poem.language, _DEFAULT_SYSTEM)
    stanza_render = render_stanzas_for_prompt(poem)
    example_text = format_examples(poem.language)
    user = USER_TEMPLATE.format(
        poem_id=poem.poem_id,
        poem_title=poem.poem_title,
        language=poem.language,
        stanza_count=len(poem.stanzas),
        stanza_render=stanza_render,
        semantic_context=json.dumps(semantic_context, ensure_ascii=False),
        recitation_styles=" | ".join(ALLOWED_RECITATION_STYLES),
        emotions=" | ".join(ALLOWED_EMOTIONS),
        tones=" | ".join(ALLOWED_TONES),
        translation_qualities=" | ".join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories=" | ".join(ALLOWED_ENTITY_CATEGORIES),
        common_rules=COMMON_RULES.format(stanza_count=len(poem.stanzas)),
        example_inputs_and_outputs=example_text,
    )
    repair = REPAIR_USER_TEMPLATE.format(
        poem_id=poem.poem_id,
        language=poem.language,
        stanza_count=len(poem.stanzas),
        stanza_render=stanza_render,
        recitation_styles="|".join(ALLOWED_RECITATION_STYLES),
        emotions="|".join(ALLOWED_EMOTIONS),
        tones="|".join(ALLOWED_TONES),
        translation_qualities="|".join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories="|".join(ALLOWED_ENTITY_CATEGORIES),
    )
    return system, user, repair


def build_gemini_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    input_json = render_prompt_input_json(poem)
    input_payload = json.loads(input_json)
    input_payload["semantic_hint"] = semantic_context
    input_json = json.dumps(input_payload, ensure_ascii=False, separators=(",", ":"))
    system = GEMINI_SYSTEM_PROMPT
    user = GEMINI_USER_TEMPLATE.format(
        stanza_count=len(poem.stanzas),
        recitation_styles="|".join(ALLOWED_RECITATION_STYLES),
        emotions="|".join(ALLOWED_EMOTIONS),
        tones="|".join(ALLOWED_TONES),
        translation_qualities="|".join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories="|".join(ALLOWED_ENTITY_CATEGORIES),
        input_json=input_json,
    )
    repair = GEMINI_REPAIR_USER_TEMPLATE.format(
        stanza_count=len(poem.stanzas),
        recitation_styles="|".join(ALLOWED_RECITATION_STYLES),
        emotions="|".join(ALLOWED_EMOTIONS),
        tones="|".join(ALLOWED_TONES),
        translation_qualities="|".join(ALLOWED_TRANSLATION_QUALITIES),
        entity_categories="|".join(ALLOWED_ENTITY_CATEGORIES),
        input_json=input_json,
    )
    return system, user, repair


def build_prompt_bundle_for_model(poem: PreprocessedPoem, model: str, semantic_context: dict) -> tuple[str, str, str]:
    if model in {"gemini", "gemini-3-flash"}:
        return build_gemini_prompt_from_preprocessed(poem, semantic_context)
    return build_prompt_from_preprocessed(poem, semantic_context)