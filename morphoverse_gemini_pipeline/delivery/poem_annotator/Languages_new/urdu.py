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
    "Urdu": GOLD_SYSTEM_PREFIX + (
        "Language hint: you are a foremost Urdu poet and classical scholar, master of the ghazal, nazm, marsiya, and qasida traditions, "
        "steeped in the Rekhta of Mir, the philosophical depth of Ghalib, the revolutionary fire of Faiz, and the lyric ache of Parveen Shakir. "
        "The radif and qafia of a ghazal are not technical features to you — they are the heartbeat. "
        "Ishq, hijr, visaal, firaaq — these are a precise philosophical vocabulary that English can only approximate. "
        "You feel the weight of the mehfil as a social form, of the maqta as the poet's signature moment, "
        "of Karbala and Husain as the eternal axis of marsiya grief. "
        "You are acutely aware that Urdu poetry carries the weight of the 1947 Partition — "
        "the loss of Lahore, the displacement of the tehzeeb of Lucknow and Delhi — "
        "and that this wound surfaces in metaphor even when not named. "
        "Named deities, saints, or legendary figures explicitly present MUST be tagged as DEITY or REGIONAL_SYMBOL as appropriate. "
        "Sufi concepts (ishq, fana, baqa, saqi, maikada) should be tagged as DEVOTIONAL_CONCEPT when used in a spiritual register. "
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

# ── Urdu examples (faithful – Tum Aaye Ho, partial – Yeh Dhoan Sa, lost – Mujhse Pehli Si) ──
URDU_EXAMPLES = [
    # faithful – Noor, clean lyric
    {
        "input": """POEM_ID: MV++_1552
LANGUAGE: Urdu
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: تم آئے ہو، نور آیا ہے، ان خوابوں کا گاؤں چاندنی میں نہایا ہے، جو رات سے پیارے ہیں، جو دن سے سنہرے ہیں، وہ خواب دکھاؤ، تم آئے ہو، نور آیا ہے
TRANSLATION: You have come, light has arrived, the village of dreams is bathed in moonlight. More beautiful than the night, brighter than the day, show me those dreams. You have come, light has arrived.
SEMANTIC_HINT: {"suggested_emotional_arc":"devotion","suggested_theme":"Love Romance","likely_cultural_terms":["نور"]}""",
        "output": json.dumps({
            "recitation_style": "devotional",
            "emotional_arc": "devotion",
            "stanzas": [{
                "index": 1,
                "emotion": "devotion",
                "tone": "prayer",
                "translation_quality": "faithful",
                "loss_note": "",
                "metaphor_spans": []
            }],
            "cultural_entities": [{"term":"نور","romanization":"Noor","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":True,"translation_note":""}]
        }, ensure_ascii=False)
    },
    # partial – dhuan/smoke, ghazal imagery diluted
    {
        "input": """POEM_ID: MV++_1556
LANGUAGE: Urdu
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: یہ دھواں سا کہاں سے اٹھتا ہے؟ دل کے جلنے کا کچھ اثر ہے کیا؟
TRANSLATION: Where does this smoky feeling rise from? Is it the sign of a burning heart?
SEMANTIC_HINT: {"suggested_emotional_arc":"grief","suggested_theme":"Philosophy","likely_cultural_terms":["دھواں","دل"]}""",
        "output": json.dumps({
            "recitation_style": "reflective",
            "emotional_arc": "grief",
            "stanzas": [{
                "index": 1,
                "emotion": "grief",
                "tone": "whisper",
                "translation_quality": "partial",
                "loss_note": "دھواں (dhuan, smoke) in the Urdu ghazal tradition is the visible trace of the burning heart — a Sufi image of love's annihilation (fana). 'Smoky feeling' domesticates this into a generic emotional register.",
                "metaphor_spans": [
                    {"source_term":"دل کے جلنے","abstract_meaning":"the heart's burning as the lover's spiritual station on the path to fana (annihilation in divine love)"}
                ]
            }],
            "cultural_entities": [{"term":"دھواں","romanization":"dhuan","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":False,"translation_note":"Sufi image of love's annihilation flattened to 'smoky feeling'."}]
        }, ensure_ascii=False)
    },
    # lost – Faiz's nazm, gham‑e‑dehr entirely lost
    {
        "input": """POEM_ID: MV++_1560
LANGUAGE: Urdu
STANZA_COUNT: 1
STANZAS:
[STANZA 1]
SOURCE: مجھ سے پہلی سی محبت مرے محبوب نہ مانگ، میں نے سمجھا تھا کہ تو ہے تو درخشاں ہے حیات، تیرا غم ہے تو غمِ دہر کا جھگڑا کیا ہے، تیری صورت سے ہے عالم میں بہاروں کو ثبات
TRANSLATION: Do not ask of me, my love, that love I once had for you. There was a time when life was bright, because you were what I wanted above all else, or so I thought. Your sorrow was mine, and so was the world's anguish.
SEMANTIC_HINT: {"suggested_emotional_arc":"grief","suggested_theme":"Social Justice","likely_cultural_terms":["غمِ دہر","فیض"]}""",
        "output": json.dumps({
            "recitation_style": "declarative",
            "emotional_arc": "grief",
            "stanzas": [{
                "index": 1,
                "emotion": "grief",
                "tone": "declaration",
                "translation_quality": "lost",
                "loss_note": "غمِ دہر (gham‑e‑dehr, the sorrow of the age/world) is the Urdu progressive literary term for collective historical suffering under colonial and class oppression — the pivot from romantic love to political consciousness that is this poem's entire meaning. 'The world's anguish' erases the specific Progressive Writers' Movement register. بہاروں کو ثبات (permanence to the springs) invokes the Urdu metaphor of bahar as political renaissance — lost entirely.",
                "metaphor_spans": []
            }],
            "cultural_entities": [
                {"term":"غمِ دہر","romanization":"gham‑e‑dehr","category":"DEVOTIONAL_CONCEPT","stanza_index":1,"preserved":False,"translation_note":"Progressive term for collective historical suffering flattened to 'world's anguish'."},
                {"term":"بہاروں کو ثبات","romanization":"baharon ko sabat","category":"REGIONAL_SYMBOL","stanza_index":1,"preserved":False,"translation_note":"Political metaphor of spring as revolutionary renaissance — omitted entirely."}
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
    example_text = format_examples(URDU_EXAMPLES)
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