from __future__ import annotations

import json

try:
    from ..config import (
        ALLOWED_RECITATION_STYLES,
        ALLOWED_EMOTIONS,
        ALLOWED_TONES,
        ALLOWED_TRANSLATION_QUALITIES,
        ALLOWED_ENTITY_CATEGORIES,
    )
    from ..dataset import PreprocessedPoem, StanzaInput
except ImportError:
    from ..config import (
        ALLOWED_RECITATION_STYLES,
        ALLOWED_EMOTIONS,
        ALLOWED_TONES,
        ALLOWED_TRANSLATION_QUALITIES,
        ALLOWED_ENTITY_CATEGORIES,
    )
    from ..dataset import PreprocessedPoem, StanzaInput

GOLD_SYSTEM_PREFIX = (
    "You are a gold-standard annotator for MorphoVerse++, a dataset of morphologically rich Indian language poems. "
    "Your annotations must be precise, conservative, text-grounded, stanza-aware, and suitable for human academic review. "
    "Do not guess. Do not hallucinate culture. Do not inflate metaphor density. Do not use generic metaphor meanings. "
    "Use the English translation for support, but keep the original-language cultural meaning as the source of truth. "
)

SYSTEM_PROMPTS = {
    "Kannada": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Kannada context carefully, including Vachana/Virashaiva poetry, Basavanna/Akkamahadevi saint tradition, "
        "Ishalinga imagery, Navodaya/Navya literary register, Kaveri/Tungabhadra river symbolism, and Hoysala/Vijayanagara heritage only when text-supported. "
        "Named saints and ishta-devatas explicitly present must not be dropped. "
        "Vachana-style direct address to Kudalasangamadeva or other lingas is DEITY, not metaphor. "
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
6. loss_note and translation_note must be short, specific, and text-grounded.
7. cultural_entities MUST include ALL culture-bearing terms found in SOURCE: named deities, devotional/philosophical concepts (karma, dharma, moksha, ishq, fana, maya, bhakti, viraha, shringar, rasa), place names and national/regional symbols (REGIONAL_SYMBOL), sacred rivers (SACRED_RIVER), festivals (FESTIVAL), musical/poetic forms like ghazal, doha, kirtan (MUSICAL_TRADITION), mythological events and epics (MYTHOLOGICAL_EVENT), and social customs (SOCIAL_CUSTOM). Expect 2-8 entities per poem.
8. Named deities explicitly present in source text MUST be included as DEITY, even if translation uses a simpler name.
9. Do not treat generic nature/body/season words as cultural entities unless the poem makes them culturally specific.
10. Relational deity epithets such as "Janaka's son-in-law" should be DEITY if they refer to the divine figure; use MYTHOLOGICAL_EVENT only when annotating an event itself.
11. metaphor_spans MUST annotate true metaphors and symbolic phrases with poem-specific meaning; aim for 1-3 per stanza where figurative language exists. source_term MUST be verbatim Indic-script text copied exactly from SOURCE — no English gloss, no romanization, no parentheses added.
12. Metaphor abstract_meaning must be poem-specific; never use generic filler like "heart = emotion" or "river = life".
13. Use [] for metaphor_spans ONLY when the stanza is purely factual or declarative with absolutely no figurative language.
14. Visual motifs are NOT required; do NOT output any visual_motifs field.
15. emotional_arc must be a concise phrase of max 8 words (e.g. "grief to peace", "longing through devotion").
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
      "index": <1-based int>,
      "emotion": "<{emotions}>",
      "tone": "<{tones}>",
      "translation_quality": "<{translation_qualities}>",
      "loss_note": "<empty string or one short sentence>",
      "metaphor_spans": [
        {{
          "source_term": "<original script word or phrase>",
          "abstract_meaning": "<one short poem-specific English phrase>"
        }}
      ]
    }}
  ],
  "cultural_entities": [
    {{
      "term": "<original script>",
      "romanization": "<short romanization or empty string>",
      "category": "<{entity_categories}>",
      "stanza_index": <1-based int>,
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

Top-level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
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
Return one minified JSON object with top-level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
Each stanza object must have: index, emotion, tone, translation_quality, loss_note, metaphor_spans.
Do NOT include visual_motifs.
Each metaphor_spans item must have: source_term, abstract_meaning.
Each cultural_entities object must have: term, romanization, category, stanza_index, preserved, translation_note.

Rules:
- Use exactly {stanza_count} stanza objects with indices 1..{stanza_count}.
- If translation_quality is faithful then loss_note="".
- metaphor_spans must be an array; use [] if none.
- Include named deities explicitly present in source text as DEITY.
- Do not return poem_id, language, stanza_count, source, translation, annotations, scene, or markdown.
- Use only these enums:
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
Top-level keys: recitation_style, emotional_arc, stanzas, cultural_entities.
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

# ── Kannada few‑shot examples (all categories valid, no "None") ──────────
KANNADA_EXAMPLES = [
    # 1. Vachana style, devotion to Ganga / river as sacred
    {
        "input": """POEM_ID: MV++_0982
LANGUAGE: Kannada
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: ಗಂಗಾ, ನಿನ್ನ ನದಿಯ ಹರಿವಿನಲ್ಲಿ
TRANSLATION: Ganga, in the flow of your river
SEMANTIC_HINT: {"suggested_emotional_arc":"devotion","suggested_theme":"Devotion","likely_cultural_terms":["ಗಂಗಾ","ನದಿ"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "devotion",
            "stanzas": [{
                "index": 1,
                "emotion": "devotion",
                "tone": "prayer",
                "translation_quality": "partial",
                "loss_note": "Ganga retains sacredness, but Virashaiva immediacy lost.",
                "metaphor_spans": [{"source_term":"ನಿನ್ನ ನದಿಯ ಹರಿವಿನಲ್ಲಿ","abstract_meaning":"immersion in sacred flow / surrender to divine rhythm"}]
            }],
            "cultural_entities": [
                {"term":"ಗಂಗಾ","romanization":"Ganga","category":"SACRED_RIVER","stanza_index":1,"preserved":True,"translation_note":""}
            ]
        }, ensure_ascii=False)
    },
    # 2. Journey / existential philosophy
    {
        "input": """POEM_ID: MV++_1005
LANGUAGE: Kannada
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: ನಡೆಯ ದಾರಿಯಲ್ಲಿ ನಿನ್ನೆ ನಾಳೆಯ ನೆನಪು
TRANSLATION: On the path of journey, memories of yesterday and tomorrow
SEMANTIC_HINT: {"suggested_emotional_arc":"longing","suggested_theme":"Philosophy","likely_cultural_terms":["ನಡೆ","ದಾರಿ","ನೆನಪು"]}""",
        "output": json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "longing",
            "stanzas": [{
                "index": 1,
                "emotion": "longing",
                "tone": "wonder",
                "translation_quality": "faithful",
                "loss_note": "",
                "metaphor_spans": [{"source_term":"ನಿನ್ನೆ ನಾಳೆಯ ನೆನಪು","abstract_meaning":"consciousness spanning time, memory holding both past and future"}]
            }],
            "cultural_entities": []
        }, ensure_ascii=False)
    },
    # 3. Land pride / patriotism
    {
        "input": """POEM_ID: MV++_0952
LANGUAGE: Kannada
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: ನಾಡಿನ ಸಿರಿತನ ಕನಸುಗಳ ನಗು ಬಾಳದಲಿ ಬೆಳಕು
TRANSLATION: The wealth of the land, the smile of dreams, light in life
SEMANTIC_HINT: {"suggested_emotional_arc":"celebration","suggested_theme":"Patriotism","likely_cultural_terms":["ನಾಡು","ಸಿರಿತನ","ಕನಸು"]}""",
        "output": json.dumps({
            "recitation_style": "celebratory",
            "emotional_arc": "celebration",
            "stanzas": [{
                "index": 1,
                "emotion": "celebration",
                "tone": "declaration",
                "translation_quality": "partial",
                "loss_note": "Siritana (splendor) loses specific Kannada cultural richness.",
                "metaphor_spans": [{"source_term":"ಕನಸುಗಳ ನಗು","abstract_meaning":"joy of aspiration / vitality of hope"}]
            }],
            "cultural_entities": [
                {"term":"ನಾಡಿನ","romanization":"nadina","category":"REGIONAL_SYMBOL","stanza_index":1,"preserved":True,"translation_note":""},
                {"term":"ಸಿರಿತನ","romanization":"siritana","category":"REGIONAL_SYMBOL","stanza_index":1,"preserved":False,"translation_note":"Splendor loses specific Kannada cultural connotation."}
            ]
        }, ensure_ascii=False)
    },
    # 4. Memorial / grief
    {
        "input": """POEM_ID: MV++_0952b
LANGUAGE: Kannada
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: ಅವನ ನೆನಪಿಗೆ ನಮನ
TRANSLATION: A salute to his memory
SEMANTIC_HINT: {"suggested_emotional_arc":"grief","suggested_theme":"Grief Loss","likely_cultural_terms":["ನೆನಪು","ನಮನ"]}""",
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
            "cultural_entities": [
                {"term":"ನೆನಪಿಗೆ","romanization":"nenapige","category":"SOCIAL_CUSTOM","stanza_index":1,"preserved":True,"translation_note":"Memorial salutation is culturally specific."}
            ]
        }, ensure_ascii=False)
    }
]

def format_examples(examples):
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"EXAMPLE {i}:\nINPUT:\n{ex['input']}\nOUTPUT:\n{ex['output']}\n")
    return "\n".join(parts)

# ── Prompt builders ───────────────────────────────────────────────────────
def build_prompt_from_preprocessed(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    system = SYSTEM_PROMPTS[poem.language]
    stanza_render = render_stanzas_for_prompt(poem)
    example_text = format_examples(KANNADA_EXAMPLES)
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