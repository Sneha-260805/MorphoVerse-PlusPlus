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
    "Bengali": GOLD_SYSTEM_PREFIX + (
        "Language hint: you are one of the greatest living Bengali poets and literary critics — "
        "scholar of Tagore, Michael Madhusudan Dutt, Jibanananda Das, and the Baul mystic tradition. "
        "Shravan is not a month but an entire emotional universe. "
        "Durga Puja, the Padma river, shonar bangla, the shadow of partition — these live in your bones. "
        "You can hear when a translation has drained the life from a Bengali metaphor "
        "and when it has miraculously preserved it. "
        "Named deities explicitly present in source text MUST be tagged as DEITY. "
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

# ── Render helpers ─────────────────────────────────────────────────────────
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

# ── Bengali few‑shot examples (faithful / partial / lost) ──────────────────
BENGALI_EXAMPLES = [
    # faithful – grief/loss, clean
    {
        "input": """POEM_ID: MV++_0027
LANGUAGE: Bengali
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: তোমার বিনা আমার দিন কাটে
একা একা আলো ছাড়া।
তোমার বিনা জীবনের পথে
যায় এক শূন্যতা।
TRANSLATION: Without you, my days pass
Alone, without light.
Without you, on the path of life,
There walks an emptiness.
SEMANTIC_HINT: {"suggested_emotional_arc":"grief","suggested_theme":"Grief Loss","likely_cultural_terms":[]}""",
        "output": json.dumps({
            "recitation_style": "lament",
            "emotional_arc": "grief",
            "stanzas": [{
                "index": 1,
                "emotion": "grief",
                "tone": "lament",
                "translation_quality": "faithful",
                "loss_note": "",
                "metaphor_spans": []
            }],
            "cultural_entities": []
        }, ensure_ascii=False)
    },
    # partial – patriotism, mixed‑language line partially lost
    {
        "input": """POEM_ID: MV++_0011
LANGUAGE: Bengali
STANZA_COUNT: 4
STANZAS:
[STANZA 1]
SOURCE: ও আমার দেশের মাটি,
তোমার কল্যাণে চাহি,
প্রাণে প্রাণে মিলে যেতে,
গানের সুরে চাহি।
[STANZA 2]
SOURCE: স্নেহের বৃষ্টি নামে,
বৃষ্টি মাথার উপর।
জীবনের পথ চলে,
শান্তির আলো তোলে।
[STANZA 3]
SOURCE: সৃষ্টির খোঁজে যাই,
তুমি আমার শিকড়।
দেশের মাটির সুরে,
পেতে চাই তোমার টান।
[STANZA 4]
SOURCE: ও আমার দেশের মাটি,
অশ্রুর নদী flows,
মা তুমি, মাটি তুমি,
সুখে থাকুক সারা জীবন।
TRANSLATION:
[STANZA 1] O soil of my country, In your welfare, I seek, To blend together in life, In the melody of songs.
[STANZA 2] The rains of affection fall, Raining upon my head. The path of life travels, Bringing forth the light of peace.
[STANZA 3] I go in search of creation, You are my roots. In the tune of the soil, I long for your embrace.
[STANZA 4] O soil of my country, The river of tears flows, Mother, you are the land, May you be happy all your life.
SEMANTIC_HINT: {"suggested_emotional_arc":"longing → peace → longing → grief","suggested_theme":"Patriotism","likely_cultural_terms":[]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "longing → peace → longing → grief",
            "stanzas": [
                {"index":1,"emotion":"longing","tone":"declaration","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":2,"emotion":"peace","tone":"tenderness","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":3,"emotion":"longing","tone":"prayer","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":4,"emotion":"grief","tone":"lament","translation_quality":"partial","loss_note":"The mixed-language line 'অশ্রুর নদী flows' (Bengali noun + English verb) is a deliberate poetic device signalling cultural rupture — the translation normalises it to plain English, erasing this formal signal of displacement.","metaphor_spans":[]}
            ],
            "cultural_entities": []
        }, ensure_ascii=False)
    },
    # lost – philosophy, Baul adrishya pathik fully erased
    {
        "input": """POEM_ID: MV++_0020
LANGUAGE: Bengali
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: যেতে যেতে দেখেছি
অদৃশ্য পথিকের কাছে এসে
মোর মনের নিকট,
আমি মৃদু মৃদু মনে মনে বলি।
একা একা চলতে গিয়ে
কত যে কথা বলি।
TRANSLATION: While going, I have seen
Coming near the invisible traveler
To my heart,
I softly speak in my mind.
Walking alone,
How many words I share.
SEMANTIC_HINT: {"suggested_emotional_arc":"longing","suggested_theme":"Philosophy","likely_cultural_terms":["অদৃশ্য পথিক"]}""",
        "output": json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "longing",
            "stanzas": [{
                "index": 1,
                "emotion": "longing",
                "tone": "whisper",
                "translation_quality": "lost",
                "loss_note": "অদৃশ্য পথিক (the invisible traveller) is a trope with deep roots in Baul and Sahajiya mystical poetry — the unseen divine companion walking alongside the soul. The translation renders it as a generic 'invisible traveler', with no mystical register, losing the entire Baul-Sahajiya devotional dimension.",
                "metaphor_spans": []
            }],
            "cultural_entities": [{
                "term": "অদৃশ্য পথিক",
                "romanization": "adrishya pathik",
                "category": "DEVOTIONAL_CONCEPT",
                "stanza_index": 1,
                "preserved": False,
                "translation_note": "The invisible traveller is a Baul-Sahajiya mystical figure representing the unseen divine companion of the soul; rendered as generic invisible traveler, the devotional-philosophical weight is entirely lost."
            }]
        }, ensure_ascii=False)
    }
]

def format_examples(examples):
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"EXAMPLE {i}:\nINPUT:\n{ex['input']}\nOUTPUT:\n{ex['output']}\n")
    return "\n".join(parts)

# ── Prompt builders ─────────────────────────────────────────────────────────
def build_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    system = SYSTEM_PROMPTS[poem.language]
    stanza_render = render_stanzas_for_prompt(poem)
    example_text = format_examples(BENGALI_EXAMPLES)
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