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
    "Telugu": GOLD_SYSTEM_PREFIX + (
        "Language hint: you are a foremost Telugu classical scholar, master of the Prabandha tradition, Carnatic music's poetic heritage, "
        "and the emotional landscape of Andhra and Telangana. "
        "Venkateshwara's presence at Tirupati, the sacred pull of the Godavari, the veena's classical weight, "
        "the koel and jasmine as cultural emblems — you feel these as living realities. "
        "Named deities such as Madhava, Krishna, Rama, Venkateshwara MUST be tagged as DEITY. "
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

# ── Telugu few‑shot examples (faithful / partial / lost) ───────────────────
TELUGU_EXAMPLES = [
    # faithful – education aphorism, no cultural entities
    {
        "input": """POEM_ID: MV++_1468
LANGUAGE: Telugu
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: చదువు అవుతుంది నీ మెదడుకు ఎరువు, ఆ ఎరువుతో వస్తుంది నీకు కొలువు, కొలువుతో తీరుతుంది నీకు కరువు, కరువు తీరి వస్తుంది నీ జీవితానికి వెలుగు, ఆ వెలుగును పది మందికి పంచి పెంచుకో నీ పరువు...
TRANSLATION: Education becomes fertilizer for your mind; with that fertilizer comes a job. With the job, your needs are fulfilled; with fulfillment, light comes to your life. Share that light with ten others, and elevate your dignity...
SEMANTIC_HINT: {"suggested_emotional_arc":"resilience","suggested_theme":"Social Justice","likely_cultural_terms":[]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "resilience",
            "stanzas": [{
                "index": 1,
                "emotion": "resilience",
                "tone": "declaration",
                "translation_quality": "faithful",
                "loss_note": "",
                "metaphor_spans": []
            }],
            "cultural_entities": []
        }, ensure_ascii=False)
    },
    # partial – farmer poem, raitanna and karuvu rakkasi partially lost
    {
        "input": """POEM_ID: MV++_1451
LANGUAGE: Telugu
STANZA_COUNT: 3
STANZAS:
[STANZA 1]
SOURCE: పగలనక రేయనక శ్రమజల్లులు కురిపించి కరముల కండలు కరిగించి బతుకు పంటను పండిస్తే..!!
[STANZA 2]
SOURCE: వారి ఆశలను నీర్జివం చేసి కరువు రక్కసి కాటేస్తుంటే హృదయలోకం చిద్రమైనది ప్రాణం శూన్యాన్ని కౌగిలించుకున్నది..!!
[STANZA 3]
SOURCE: దేశ ప్రజల ఆకలి కేకలను తీర్చి ఆ రైతన్న ఆకాశంలోకి ఆవిరైపోతున్నా ఆ కష్టజీవి గుండెపోటుకు కారణం ఈ దగకోరుల వెన్నుపోటే కదా..!!
TRANSLATION:
[STANZA 1] Day or night, he pours out showers of sweat, with calloused hands melting away, he nurtures the crops of life...!!
[STANZA 2] When his hopes dry up and the drought demon devours, his heart becomes shattered, embracing the emptiness of life...!!
[STANZA 3] Feeding the hunger of the nation, the farmer evaporates into the sky, but the cause of his heart's collapse is the treachery of those who betrayed him...!!
SEMANTIC_HINT: {"suggested_emotional_arc":"resilience → grief → anger","suggested_theme":"Social Justice","likely_cultural_terms":["కరువు రక్కసి","రైతన్న"]}""",
        "output": json.dumps({
            "recitation_style": "lament",
            "emotional_arc": "resilience → grief → anger",
            "stanzas": [
                {
                    "index": 1,
                    "emotion": "resilience",
                    "tone": "declaration",
                    "translation_quality": "faithful",
                    "loss_note": "",
                    "metaphor_spans": []
                },
                {
                    "index": 2,
                    "emotion": "grief",
                    "tone": "lament",
                    "translation_quality": "partial",
                    "loss_note": "కరువు రక్కసి (drought demon) is a specific Telugu folk‑mythological figure — the demon of drought personified as a devouring rakshasa; 'drought demon' approximates it but loses the regional folk‑mythological specificity.",
                    "metaphor_spans": []
                },
                {
                    "index": 3,
                    "emotion": "anger",
                    "tone": "declaration",
                    "translation_quality": "partial",
                    "loss_note": "రైతన్న (raitanna — farmer‑brother) is a term of collective solidarity unique to Telugu social discourse; rendered as generic 'farmer', the kinship‑solidarity register is lost.",
                    "metaphor_spans": []
                }
            ],
            "cultural_entities": [
                {
                    "term": "కరువు రక్కసి",
                    "romanization": "karuvu rakkasi",
                    "category": "MYTHOLOGICAL_EVENT",
                    "stanza_index": 2,
                    "preserved": False,
                    "translation_note": "Drought demon is a folk‑mythological Telugu figure; approximated in translation but the rakkasi (rakshasa/demon) register of Telugu folk belief is softened."
                },
                {
                    "term": "రైతన్న",
                    "romanization": "raitanna",
                    "category": "SOCIAL_CUSTOM",
                    "stanza_index": 3,
                    "preserved": False,
                    "translation_note": "Raitanna (farmer‑brother) is a term of collective solidarity unique to Telugu social culture; rendered as generic 'farmer', the kinship address is erased."
                }
            ]
        }, ensure_ascii=False)
    },
    # lost – Evareevaro, pallavi refrain device fully lost
    {
        "input": """POEM_ID: MV++_1452
LANGUAGE: Telugu
STANZA_COUNT: 5
STANZAS:
[STANZA 1]
SOURCE: ఎవరో... ఎవరో... నీవెవరో
[STANZA 2]
SOURCE: పూవై రాలిన తారకవో ఆమని పాడిన గీతికవో నీవొక సుందర స్వపికవో ఎవరో... ఎవరో... నీవెవరో......
[STANZA 3]
SOURCE: వేసవి వేకువలో అరవిరిసిన స్నిగ్ధసుగంధ మందారానివో కోయిల రాగంలో పలికిన కోటివీణల స్వరమంత్రాక్షరివో నేనే నీవై తనువు మనసు కలలో ఇలలో తహతహలాడుతు తపస్సు చేసే ఉషస్సు నీవో....
[STANZA 4]
SOURCE: ఆగని మనసుల ఆరాటంలో ఎగిసే తలపుల పోరాటంలో అందని జాబిలి వెన్నెల నీవో గుండెల నిండిన పండుగ నీవో.......
[STANZA 5]
SOURCE: ఎవరో... ఎవరో... నీవెవరో
TRANSLATION:
[STANZA 1] Who Are You... Who Are You... Who Are You?
[STANZA 2] A star that withered like a flower, or a melody sung by the sky? Are you a beautiful dream? Who are you... who are you... who are you?
[STANZA 3] In the early dawn of summer, are you the gently fragrant mandara, fully bloomed? Or the magical notes of a million veenas played in the tune of a koel's song? I become you, body and soul, trembling in dreams and reality, like the dawn performing penance for you...
[STANZA 4] In the restless struggle of hearts, in the battle of rising thoughts, you are the unreachable moonlight, you are the festival filling my heart...
[STANZA 5] Who are you... who are you... who are you?
SEMANTIC_HINT: {"suggested_emotional_arc":"longing → longing → devotion → longing → longing","suggested_theme":"Love Romance","likely_cultural_terms":["మందారం","కోయిల","వీణ"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "longing → longing → devotion → longing → longing",
            "stanzas": [
                {"index":1,"emotion":"longing","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":2,"emotion":"longing","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[]},
                {"index":3,"emotion":"devotion","tone":"prayer","translation_quality":"partial","loss_note":"తపస్సు చేసే ఉషస్సు (dawn performing penance) is a Sanskrit‑rooted devotional metaphor equating the speaker's longing with ascetic tapas — the translation captures the image but loses the Carnatic devotional register of tapasya as spiritual discipline.","metaphor_spans":[]},
                {"index":4,"emotion":"longing","tone":"lament","translation_quality":"partial","loss_note":"పండుగ (festival) in Telugu carries a collective, sacred‑communal connotation tied to community ritual — rendered as generic 'festival filling my heart', the communal‑sacred dimension is lost.","metaphor_spans":[]},
                {"index":5,"emotion":"longing","tone":"wonder","translation_quality":"lost","loss_note":"The Telugu refrain ఎవరో carries a specific emotional resonance — its repetition is a classical Telugu lyric device (pallavi) signalling unresolved longing. 'Who are you' is phonetically equivalent but the pallavi structural weight is entirely lost.","metaphor_spans":[]}
            ],
            "cultural_entities": [
                {"term":"మందారం","romanization":"mandara","category":"REGIONAL_SYMBOL","stanza_index":3,"preserved":True,"translation_note":""},
                {"term":"కోయిల","romanization":"koel","category":"REGIONAL_SYMBOL","stanza_index":3,"preserved":True,"translation_note":""},
                {"term":"వీణ","romanization":"veena","category":"MUSICAL_TRADITION","stanza_index":3,"preserved":True,"translation_note":""}
            ]
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
    example_text = format_examples(TELUGU_EXAMPLES)
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