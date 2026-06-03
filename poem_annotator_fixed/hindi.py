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

# ----------------------------------------------------------------------
# 1. System prompt (unchanged)
# ----------------------------------------------------------------------
GOLD_SYSTEM_PREFIX = (
    "You are a gold-standard annotator for MorphoVerse++, a dataset of morphologically rich Indian language poems. "
    "Your annotations must be precise, conservative, text-grounded, stanza-aware, and suitable for human academic review. "
    "Do not guess. Do not hallucinate culture. Do not inflate metaphor density. Do not use generic metaphor meanings. "
    "Use the English translation for support, but keep the original-language cultural meaning as the source of truth. "
)

SYSTEM_PROMPTS = {
    "Hindi": GOLD_SYSTEM_PREFIX + (
        "Language hint: read Hindi/Sanskrit-rooted devotional context carefully, including Ramayana, Mahabharata, Bhakti, dharma, vanavas, moksha only when text-supported. "
        "Named deities such as Ram, Krishna, Sita, Madhava, Vishnu MUST be tagged as DEITY. "
        "THIS IS HINDI. DO NOT CONFUSE WITH URDU OR BENGALI. "
        "Return one valid JSON object only. No explanation, no markdown."
    ),
}

# ----------------------------------------------------------------------
# 2. Rules (visual_motifs removed, schema enforced)
# ----------------------------------------------------------------------
COMMON_RULES = """\
RULES:
1. Return JSON only. No markdown, no prose outside JSON.
2. Use exactly the allowed labels for recitation_style, emotion, tone, translation_quality, and category.
3. Do not add extra fields and do not output scene.
4. Use exactly {stanza_count} stanza objects and keep indices 1..{stanza_count}.
5. If translation_quality is faithful, loss_note must be "".
6. loss_note and translation_note must be short, specific, and text-grounded.
7. cultural_entities must include only explicit or strongly implied culture-bearing terms.
8. Named deities explicitly present in source text MUST be included as DEITY, even if translation uses a simpler name.
9. Do not treat generic nature/body/season words as cultural entities unless the poem makes them culturally specific.
10. Relational deity epithets such as "Janaka's son-in-law" should be DEITY if they refer to the divine figure; use MYTHOLOGICAL_EVENT only when annotating an event itself.
11. metaphor_spans must include only true metaphors/symbolic phrases, not every poetic noun.
12. Metaphor abstract_meaning must be poem-specific; never use generic filler like "heart = emotion" or "river = life".
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

# ── Hindi few‑shot examples (all enums valid, no extra fields) ───────────
HINDI_EXAMPLES = [
    # 1. Devotional stotra – Tulsidas Ramacharitmanas couplet
    {
        "input": """POEM_ID: MV++_0056
LANGUAGE: Hindi
STANZA_COUNT: 2
STANZAS:
[STANZA 1]
SOURCE: श्री रामचंद्र कृपालु भजु मन हरण भव भय दारुणं।
TRANSLATION: O mind, sing the praises of compassionate Lord Ram,
[STANZA 2]
SOURCE: कन्दर्प अगणित अमित छवि नव नील नीरद सुन्दरं।
TRANSLATION: He is as charming as a newly formed dark cloud,
SEMANTIC_HINT: {"suggested_emotional_arc":"devotion","suggested_theme":"Devotion","likely_cultural_terms":["रामचंद्र","भव भय","कन्दर्प","जनक सुतावरं"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "devotion",
            "stanzas": [
                {
                    "index": 1,
                    "emotion": "devotion",
                    "tone": "prayer",
                    "translation_quality": "partial",
                    "loss_note": "Bhav bhay loses samsaric terror nuance.",
                    "metaphor_spans": []
                },
                {
                    "index": 2,
                    "emotion": "devotion",
                    "tone": "wonder",
                    "translation_quality": "partial",
                    "loss_note": "Kandarp rendered as Cupid dilutes devotional register.",
                    "metaphor_spans": []
                }
            ],
            "cultural_entities": [
                {"term":"श्री रामचंद्र","romanization":"Shri Ramchandra","category":"DEITY","stanza_index":1,"preserved":True,"translation_note":"Lord Ram is retained, honorific Shri lost."},
                {"term":"भव भय","romanization":"bhav bhay","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":False,"translation_note":"Samsaric fear flattened to worldly existence."},
                {"term":"कन्दर्प","romanization":"kandarpa","category":"DEITY","stanza_index":2,"preserved":True,"translation_note":"God of love correctly equated to Cupid."},
                {"term":"जनक सुतावरं","romanization":"Janak sutavaram","category":"MYTHOLOGICAL_EVENT","stanza_index":2,"preserved":True,"translation_note":"Sita's swayamvar reference preserved."}
            ]
        }, ensure_ascii=False)
    },
    # 2. Romantic/Patriotic – Chitthi Aayi Hai (exile, longing)
    {
        "input": """POEM_ID: MV++_0059
LANGUAGE: Hindi
STANZA_COUNT: 2
STANZAS:
[STANZA 1]
SOURCE: चिट्ठी आई है वतन से चिट्ठी आई है
TRANSLATION: A letter has arrived, a letter from home has arrived
[STANZA 2]
SOURCE: आंखों में पानी लेकर हमने चिट्ठी खोली
TRANSLATION: With tears in our eyes we opened the letter
SEMANTIC_HINT: {"suggested_emotional_arc":"longing → grief","suggested_theme":"Patriotism","likely_cultural_terms":["वतन","बेवतन","मिट्टी","चांद"]}""",
        "output": json.dumps({
            "recitation_style": "lament",
            "emotional_arc": "longing → grief",
            "stanzas": [
                {"index":1,"emotion":"longing","tone":"lament","translation_quality":"partial","loss_note":"Bevatan loses specific exile anguish.","metaphor_spans":[]},
                {"index":2,"emotion":"grief","tone":"tenderness","translation_quality":"faithful","loss_note":"","metaphor_spans":[]}
            ],
            "cultural_entities": [
                {"term":"वतन","romanization":"vatan","category":"REGIONAL_SYMBOL","stanza_index":1,"preserved":False,"translation_note":"Home loses vatan's sacred motherland weight."},
                {"term":"बेवतन","romanization":"bevatan","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":False,"translation_note":"Exile flattens sense of being without a homeland."},
                {"term":"वतन की मिट्टी","romanization":"vatan ki mitti","category":"REGIONAL_SYMBOL","stanza_index":1,"preserved":False,"translation_note":"Sacred soil reduced to ordinary earth."},
                {"term":"चांद","romanization":"chaand","category":"REGIONAL_SYMBOL","stanza_index":2,"preserved":True,"translation_note":"Shared moon motif preserved."}
            ]
        }, ensure_ascii=False)
    },
    # 3. Protest/Internal exile – Doosra Banwas (Ramayana)
    {
        "input": """POEM_ID: MV++_0477
LANGUAGE: Hindi
STANZA_COUNT: 4
STANZAS:
[STANZA 1]
SOURCE: वनवास का दर्द सहा था एक बार,
TRANSLATION: Once the pain of exile was endured,
[STANZA 2]
SOURCE: वो था सीता का बेटा,
TRANSLATION: He was Sita's son,
[STANZA 3]
SOURCE: पर इस बार बनवास का दर्द,
TRANSLATION: But this time the pain of exile,
[STANZA 4]
SOURCE: धरती माँ ने रोकर कहा,
TRANSLATION: Mother Earth wept and said,
SEMANTIC_HINT: {"suggested_emotional_arc":"grief","suggested_theme":"Grief Loss","likely_cultural_terms":["वनवास","राम","सीता","धरती माँ"]}""",
        "output": json.dumps({
            "recitation_style": "lament",
            "emotional_arc": "grief → grief → grief → grief",
            "stanzas": [
                {"index":1,"emotion":"grief","tone":"lament","translation_quality":"partial","loss_note":"Vanavas loses Ramayana-specific exile weight.","metaphor_spans":[]},
                {"index":2,"emotion":"grief","tone":"tenderness","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":3,"emotion":"grief","tone":"lament","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":4,"emotion":"grief","tone":"lament","translation_quality":"partial","loss_note":"Dharti Maa as living myth of Sita swallowed by earth lost.","metaphor_spans":[]}
            ],
            "cultural_entities": [
                {"term":"वनवास","romanization":"vanavas","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":False,"translation_note":"Sacred exile flattened to generic exile."},
                {"term":"राम","romanization":"Ram","category":"DEITY","stanza_index":1,"preserved":True,"translation_note":""},
                {"term":"सीता","romanization":"Sita","category":"DEITY","stanza_index":1,"preserved":True,"translation_note":""},
                {"term":"धरती माँ","romanization":"Dharti Maa","category":"MYTHOLOGICAL_EVENT","stanza_index":4,"preserved":False,"translation_note":"Mother Earth reduced to generic metaphor; Ramayana event erased."}
            ]
        }, ensure_ascii=False)
    },
    # 4. Nature / peace – Saanjh Ka Geet (no cultural entities)
    {
        "input": """POEM_ID: MV++_0791
LANGUAGE: Hindi
STANZA_COUNT: 3
STANZAS:
[STANZA 1]
SOURCE: सांझ के रंगों में डूबा,
TRANSLATION: Drenched in the hues of evening,
[STANZA 2]
SOURCE: आसमान के आँचल तले,
TRANSLATION: Beneath the sky's vast embrace,
[STANZA 3]
SOURCE: यह गीत सांझ का है,
TRANSLATION: This is the song of the evening,
SEMANTIC_HINT: {"suggested_emotional_arc":"peace","suggested_theme":"Nature","likely_cultural_terms":[]}""",
        "output": json.dumps({
            "recitation_style": "lament",
            "emotional_arc": "peace",
            "stanzas": [
                {"index":1,"emotion":"peace","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[{"source_term":"सांझ के रंगों में डूबा","abstract_meaning":"being immersed in the sensory richness of evening"}]},
                {"index":2,"emotion":"peace","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[{"source_term":"आसमान के आँचल तले","abstract_meaning":"sky as a protective maternal canopy"}]},
                {"index":3,"emotion":"peace","tone":"tenderness","translation_quality":"faithful","loss_note":"","metaphor_spans":[]}
            ],
            "cultural_entities": []
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
    example_text = format_examples(HINDI_EXAMPLES)
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