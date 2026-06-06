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
    "Santhali": GOLD_SYSTEM_PREFIX + (
        "Language hint: Santhali is an Austro‑Asiatic (Munda) language with an overwhelmingly oral poetic tradition and a scarce written corpus. "
        "Read context carefully for Bonga spirit worship (Marang Buru, Jaher‑era nature spirits), Sohrai/Karma/Baha festival imagery, Dhol/Tamak drum rhythms, "
        "forest/paddy field landscape, and the Hul rebellion/Sido‑Kanhu historical resonance only when text‑supported. "
        "IMPORTANT: THIS IS SANTHALI, NOT HINDI OR BENGALI. Annotate strictly from Santhali tribal cosmology and oral tradition. "
        "Do not import Indic Hindu or Sanskrit cultural frameworks; Santhali cosmology is distinct. "
        "Given corpus scarcity, prefer maximally conservative annotation. Flag cultural_entities only when the term is unambiguously culture‑bearing in the source text. "
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


# ── Santhali examples (all invalid enums replaced) ─────────────────────────
SANTHALI_EXAMPLES = [
    # 1. Santhal Rebellion – resistance, historical
    {
        "input": """POEM_ID: MV++_1238
LANGUAGE: Santhali
STANZA_COUNT: 2
STANZAS:
[STANZA 1]
SOURCE: संताल, ज़मीन, आज़ादी
TRANSLATION: Santhal, land, freedom
[STANZA 2]
SOURCE: संताल की आवाज़, गूंजेगी सदा
TRANSLATION: The voice of the Santhal, will echo forever
SEMANTIC_HINT: {"suggested_emotional_arc":"rebellion","suggested_theme":"Patriotism","likely_cultural_terms":["संताल","ज़मीन","आज़ादी","गूंजेगी"]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "rebellion",
            "stanzas": [
                {
                    "index": 1,
                    "emotion": "anger",
                    "tone": "defiance",
                    "translation_quality": "partial",
                    "loss_note": "Azadi carries anti‑colonial weight; 'freedom' generic.",
                    "metaphor_spans": [
                        {"source_term": "ज़मीन", "abstract_meaning": "ancestral land as the very identity of the Santhal people, not just territory"}
                    ]
                },
                {
                    "index": 2,
                    "emotion": "anger",
                    "tone": "declaration",
                    "translation_quality": "partial",
                    "loss_note": "Gūnjegi sadā loses the tribal oral echo and the communal voice of resistance.",
                    "metaphor_spans": [
                        {"source_term": "गूंजेगी सदा", "abstract_meaning": "eternal resonance of the collective voice, a promise of undying memory"}
                    ]
                }
            ],
            "cultural_entities": [
                {"term": "संताल", "romanization": "Santhal", "category": "REGIONAL_SYMBOL", "stanza_index": 1, "preserved": True, "translation_note": ""},
                {"term": "ज़मीन", "romanization": "zameen", "category": "REGIONAL_SYMBOL", "stanza_index": 1, "preserved": False, "translation_note": "Land reduced to generic; tribal ancestral territory meaning lost."}
            ]
        }, ensure_ascii=False)
    },
    # 2. Dalkhata – fisherman, humble labour, nature
    {
        "input": """POEM_ID: MV++_1237
LANGUAGE: Santhali
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: डालखाता, नदी की लहरों में, चंचल जल की धारा, सपने सजाए ले जाता
TRANSLATION: The fisherman, in the river waves, the playful stream carries dreams adorned
SEMANTIC_HINT: {"suggested_emotional_arc":"peace","suggested_theme":"Nature","likely_cultural_terms":["नदी"]}""",
        "output": json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "peace",
            "stanzas": [{
                "index": 1,
                "emotion": "peace",
                "tone": "tenderness",
                "translation_quality": "partial",
                "loss_note": "Dalkhata is a specific folk archetype; 'fisherman' loses the cultural identity.",
                "metaphor_spans": [
                    {"source_term": "चंचल जल की धारा", "abstract_meaning": "the playful stream as a carrier of fragile hopes and aspirations"},
                    {"source_term": "सपने सजाए", "abstract_meaning": "dreams adorned and gently carried away by life's currents"}
                ]
            }],
            "cultural_entities": [
                {"term": "डालखाता", "romanization": "Dalkhata", "category": "REGIONAL_SYMBOL", "stanza_index": 1, "preserved": False, "translation_note": "Specific Santhali folk archetype lost."}
            ]
        }, ensure_ascii=False)
    },
    # 3. Jitna Pahar – collective climb, solidarity
    {
        "input": """POEM_ID: MV++_1239
LANGUAGE: Santhali
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: जितना पहाड़, उतना अडिग संकल्प, हाथ में हाथ हो
TRANSLATION: As big as the mountain, that firm the resolve, hand in hand
SEMANTIC_HINT: {"suggested_emotional_arc":"resilience","suggested_theme":"Resilience","likely_cultural_terms":["पहाड़","संकल्प"]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "resilience",
            "stanzas": [{
                "index": 1,
                "emotion": "resilience",
                "tone": "declaration",
                "translation_quality": "faithful",
                "loss_note": "",
                "metaphor_spans": [
                    {"source_term": "पहाड़", "abstract_meaning": "obstacle proportionate to the strength of collective will"},
                    {"source_term": "हाथ में हाथ", "abstract_meaning": "solidarity as the foundation of overcoming – hands joined represent unbreakable community"}
                ]
            }],
            "cultural_entities": []
        }, ensure_ascii=False)
    },
    # 4. Bonga invocation – sparse, conservative annotation
    {
        "input": """POEM_ID: MV++_1240
LANGUAGE: Santhali
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: मारङ बुरु देवता, जोहार, सोहराय गीत
TRANSLATION: Marang Buru deity, greetings, Sohrai song
SEMANTIC_HINT: {"suggested_emotional_arc":"reverence","suggested_theme":"Devotion","likely_cultural_terms":["मारङ बुरु","सोहराय"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "reverence",
            "stanzas": [{
                "index": 1,
                "emotion": "devotion",
                "tone": "prayer",
                "translation_quality": "partial",
                "loss_note": "Marang Buru loses status as supreme mountain deity; Sohrai festival context missing.",
                "metaphor_spans": []
            }],
            "cultural_entities": [
                {"term": "मारङ बुरु", "romanization": "Marang Buru", "category": "DEITY", "stanza_index": 1, "preserved": False, "translation_note": "Supreme Santhali mountain spirit reduced to generic deity."},
                {"term": "सोहराय", "romanization": "Sohrai", "category": "FESTIVAL", "stanza_index": 1, "preserved": False, "translation_note": "Harvest festival removed; renders song generic."}
            ]
        }, ensure_ascii=False)
    }
]

def format_examples(examples):
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"EXAMPLE {i}:\nINPUT:\n{ex['input']}\nOUTPUT:\n{ex['output']}\n")
    return "\n".join(parts)


# ── Prompt builders (unchanged except passing examples) ────────────────────
def build_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    system = SYSTEM_PROMPTS[poem.language]
    stanza_render = render_stanzas_for_prompt(poem)
    example_text = format_examples(SANTHALI_EXAMPLES)
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