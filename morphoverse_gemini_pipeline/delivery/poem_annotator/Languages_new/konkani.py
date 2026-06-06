from __future__ import annotations

import json

try:
    from .config import (
        ALLOWED_RECITATION_STYLES,
        ALLOWED_EMOTIONS,
        ALLOWED_TONES,
        ALLOWED_TRANSLATION_QUALITIES,
        ALLOWED_ENTITY_CATEGORIES,
    )
    from .dataset import PreprocessedPoem, StanzaInput
except ImportError:
    from config import (
        ALLOWED_RECITATION_STYLES,
        ALLOWED_EMOTIONS,
        ALLOWED_TONES,
        ALLOWED_TRANSLATION_QUALITIES,
        ALLOWED_ENTITY_CATEGORIES,
    )
    from dataset import PreprocessedPoem, StanzaInput

GOLD_SYSTEM_PREFIX = (
    "You are a gold‑standard annotator for MorphoVerse++, a dataset of morphologically rich Indian language poems. "
    "Your annotations must be precise, conservative, text‑grounded, stanza‑aware, and suitable for human academic review. "
    "Do not guess. Do not hallucinate culture. Do not inflate metaphor density. Do not use generic metaphor meanings. "
    "Use the English translation for support, but keep the original‑language cultural meaning as the source of truth. "
)

SYSTEM_PROMPTS = {
    "Konkani": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Konkani context carefully, including Goan Catholic tradition (Feast of St. Francis Xavier, mandó song form), "
        "Saraswat Hindu tradition (Mahalakshmi/Shantadurga, Gaud Saraswat rituals), Mandovi/Zuari river imagery, and coastal/monsoon landscape only when text‑supported. "
        "IMPORTANT: THIS IS KONKANI, NOT MARATHI. Annotate strictly from Konkani cultural markers, not Marathi ones. "
        "Konkani poetry may code‑switch between Catholic and Hindu registers; annotate strictly according to what the text supports. "
        "Script variants do not change annotation rules. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
}

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

# Konkani examples – normalized to allowed enums
KONKANI_EXAMPLES = [
    # 1. Dakhlo – pinch of salt, humility
    {
        "input": """POEM_ID: MV++_1168
LANGUAGE: Konkani
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: डाखलो साल्ट, संपूर्ण जगात सोडून देतं, जीवन स्वाद आणता
TRANSLATION: A pinch of salt, leaving everything behind in the whole world, it brings flavor to life
SEMANTIC_HINT: {"suggested_emotional_arc":"acceptance","suggested_theme":"Philosophy","likely_cultural_terms":["डाखलो","साल्ट"]}""",
        "output": json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "peace",
            "stanzas": [{
                "index": 1,
                "emotion": "peace",
                "tone": "tenderness",
                "translation_quality": "partial",
                "loss_note": "Dakhlo, a uniquely Konkani expression for 'a pinch', loses its culinary‑folk minimalism.",
                "metaphor_spans": [
                    {"source_term": "डाखलो साल्ट", "abstract_meaning": "insignificant self that paradoxically seasons the whole of existence with meaning"},
                    {"source_term": "सोडून देतं", "abstract_meaning": "renunciation of attachment / letting go of the ego in the vastness of the world"}
                ]
            }],
            "cultural_entities": [
                {"term": "डाखलो", "romanization": "dakhlo", "category": "SOCIAL_CUSTOM", "stanza_index": 1, "preserved": False, "translation_note": "Local phrase for 'a pinch' lost."}
            ]
        }, ensure_ascii=False)
    },
    # 2. Zali Vhalan – romantic arrival
    {
        "input": """POEM_ID: MV++_1167
LANGUAGE: Konkani
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: झली व्हालं आला, संपूर्ण आकाशाचं गौरव करून, प्रत्येक फुशीत तुला प्रिय करतो
TRANSLATION: The lover came, honoring the entire sky, in every whisper I cherish you
SEMANTIC_HINT: {"suggested_emotional_arc":"joy","suggested_theme":"Love Romance","likely_cultural_terms":["आकाश","फुशी"]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "celebration",
            "stanzas": [{
                "index": 1,
                "emotion": "celebration",
                "tone": "prayer",
                "translation_quality": "partial",
                "loss_note": "Zhali vhalan's folk intimacy and the Goan romantic register diluted.",
                "metaphor_spans": [
                    {"source_term": "आकाशाचं गौरव", "abstract_meaning": "beloved's presence elevates the cosmos to celestial significance"},
                    {"source_term": "प्रत्येक फुशीत", "abstract_meaning": "tenderness communicated in the smallest breath / love in every whisper"}
                ]
            }],
            "cultural_entities": [
                {"term": "फुशी", "romanization": "phushi", "category": "SOCIAL_CUSTOM", "stanza_index": 1, "preserved": False, "translation_note": "Whisper as intimate Konkani communication lost."}
            ]
        }, ensure_ascii=False)
    },
    # 3. Dev Boren – faith, collective hope
    {
        "input": """POEM_ID: MV++_1169
LANGUAGE: Konkani
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: देव बोरें आम्हां, जिवंत ठेवील, संपूर्ण आकाशात उगवलेली आशा
TRANSLATION: God will save us, keep us alive, hope rising in the vast sky
SEMANTIC_HINT: {"suggested_emotional_arc":"hope","suggested_theme":"Devotion","likely_cultural_terms":["देव","आशा"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "devotion",
            "stanzas": [{
                "index": 1,
                "emotion": "devotion",
                "tone": "prayer",
                "translation_quality": "partial",
                "loss_note": "Amhan ('us') carries the weight of Konkani diaspora and minority community; collective identity weakened.",
                "metaphor_spans": [
                    {"source_term": "जिवंत ठेवील", "abstract_meaning": "divine life‑sustenance / grace as survival"},
                    {"source_term": "आकाशात उगवलेली आशा", "abstract_meaning": "hope ascending to heaven / prayer rising like dawn"}
                ]
            }],
            "cultural_entities": [
                {"term": "देव", "romanization": "dev", "category": "DEITY", "stanza_index": 1, "preserved": True, "translation_note": "God retained, but the specific Catholic or Hindu identity ambiguous."}
            ]
        }, ensure_ascii=False)
    },
    # 4. Goan monsoon mandó – rain and music
    {
        "input": """POEM_ID: MV++_1170
LANGUAGE: Konkani
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: पावसाचे राती, मांडवाच्या सावळी, सोबित कान्तार गायतात
TRANSLATION: On rainy nights, in the shade of the mandó, they sing beautiful songs
SEMANTIC_HINT: {"suggested_emotional_arc":"longing","suggested_theme":"Nature","likely_cultural_terms":["मांडो","कान्तार"]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "longing",
            "stanzas": [{
                "index": 1,
                "emotion": "longing",
                "tone": "lament",
                "translation_quality": "partial",
                "loss_note": "Mandó is a specific Goan song form, a cultural institution; 'shade of the mandó' obscures this.",
                "metaphor_spans": [
                    {"source_term": "मांडवाच्या सावळी", "abstract_meaning": "the mandó gathering as a shelter for the soul, where music becomes a communal refuge"}
                ]
            }],
            "cultural_entities": [
                {"term": "मांडो", "romanization": "mando", "category": "MUSICAL_TRADITION", "stanza_index": 1, "preserved": False, "translation_note": "Goan musical tradition completely lost."},
                {"term": "कान्तार", "romanization": "kantar", "category": "MUSICAL_TRADITION", "stanza_index": 1, "preserved": False, "translation_note": "Folk song rendered generic."}
            ]
        }, ensure_ascii=False)
    }
]

def format_examples(examples):
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"EXAMPLE {i}:\nINPUT:\n{ex['input']}\nOUTPUT:\n{ex['output']}\n")
    return "\n".join(parts)


def build_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    system = SYSTEM_PROMPTS[poem.language]
    stanza_render = render_stanzas_for_prompt(poem)
    example_text = format_examples(KONKANI_EXAMPLES)
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