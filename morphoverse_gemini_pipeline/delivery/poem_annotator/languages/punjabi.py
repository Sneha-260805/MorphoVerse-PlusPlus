"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Punjabi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ਅੱਜ ਆਖਾਂ ਵਾਰਿਸ ਸ਼ਾਹ ਨੂੰ, ਕਿਤੋਂ ਕਬਰਾਂ ਵਿੱਚੋਂ ਬੋਲ, ਤੇ ਅੱਜ ਕਿਤਾਬ-ਏ-ਇਸ਼ਕ ਦਾ, ਕੋਈ ਅਗਲਾ ਵਰਕਾ ਫੋਲ, ਇੱਕ ਰੋਈ ਸੀ ਧੀ ਪੰਜਾਬ ਦੀ, ਤੂੰ ਲਿਖ ਲਿਖ ਮਾਰੇ ਵੈਨ, ਅੱਜ ਲੱਖਾਂ ਧੀਆਂ ਰੋ ਰਹੀਆਂ, ਤੈਨੂੰ ਵਾਰਿਸ ਸ਼ਾਹ ਨੂੰ ਕਹਿਨ\nTranslation: Today, I call Waris Shah, speak from your grave, and turn to the next page of the book of love. Once, a daughter of Punjab wept, and you wrote a long saga of pain. Today, a million daughters cry to you, Waris Shah, speak up again.",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "ਕਿਤਾਬ-ਏ-ਇਸ਼ਕ (Kitaab‑e‑Ishq) is not a generic 'book of love' but a direct reference to Waris Shah's Heer Ranjha — the foundational Punjabi romance epic; 'book of love' loses the intertextual invocation of Punjab's greatest literary monument. ਵੈਨ (vain), the Punjabi lamentation‑cry, is rendered as 'saga of pain' but is actually a specific oral mourning form performed by women.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "ਵਾਰਿਸ ਸ਼ਾਹ",
          "romanization": "Waris Shah",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "ਕਿਤਾਬ-ਏ-ਇਸ਼ਕ",
          "romanization": "Kitaab‑e‑Ishq",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'book of love' — loses the specific Heer Ranjha reference."
        },
        {
          "term": "ਵੈਨ",
          "romanization": "vain",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Punjabi women's mourning form flattened to 'saga of pain'."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Punjabi\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: ਮੇਰੀ ਨਮ ਭਿੱਜੀ ਮਿੱਟੀ ਨੂੰ ਕਿੰਨਾ ਸੁੰਦਰ ਗੂੰਧਿਆ ਸੀ, ਇੱਕ ਘੜਾ ਬਣਾਇਆ ਸੀ, ਜੋ ਦੂਰ ਦੇ ਪਿੰਡਾਂ ਨੂੰ ਜਾਂਦਾ ਸੀ, ਪਰ ਮੇਰੇ ਹੀ ਝੋਨੇ ਵਿੱਚੋਂ ਪਾਣੀ ਲੈ ਕੇ।\n[STANZA 2]\nSOURCE: ਫਿਰ ਇੱਕ ਦਿਨ ਘੜਾ ਟੁੱਟ ਗਿਆ, ਤੇ ਮੈਂ ਸਿਰਫ ਢੇਰੀ ਹੀ ਰਹਿ ਗਿਆ, ਮਿੱਟੀ ਦੀ ਢੇਰੀ।\nTRANSLATION:\n[STANZA 1] My moist, wet clay was shaped so beautifully into a pitcher that traveled to distant lands but carried water from my own well.\n[STANZA 2] One day, the pitcher broke and I remained just a heap of clay.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "grief → resignation",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Punjabi\nSTANZA_COUNT: 3\nSTANZAS:\n[STANZA 1]\nSOURCE: ਇਕ ਚਾਦਰ ਮੈਲੀ ਸੀ, ਜੋ ਅਕਸਰ ਮੈਨੂੰ ਢੱਕਦੀ ਰਹੀ, ਮੈਂ ਉਸੇ ਵਿਚ ਸਮਾਈ, ਉਸੇ ਦੀ ਗਲੀਆਂ ਵਿਚ ਰਾਹ ਪਾਇਆ।\n[STANZA 2]\nSOURCE: ਕਈ ਜਖ਼ਮਾਂ ਦੇ ਨਿਸ਼ਾਨ, ਉਸ ਚਾਦਰ 'ਤੇ ਛੁਪੇ ਹੋਏ ਸਨ, ਕਦੇ ਉਹ ਮੈਨੂੰ ਤਸੱਲੀ ਦਿੰਦੀ, ਕਦੇ ਰੋਣ ਵਾਲਾ ਬਣਾਇਆ।\n[STANZA 3]\nSOURCE: ਮੇਰਾ ਰਾਹ ਉਸੇ ਚਾਦਰ ਵਿਚ ਸੀ, ਮੇਰੀ ਥਕਾਵਟ ਉਸੇ ਵਿਚ ਸੀ, ਇਕ ਚਾਦਰ ਮੈਲੀ ਸੀ, ਜਿਸ ਨੇ ਮੈਨੂੰ ਕਹਾਣੀਆਂ ਵਿੱਚ ਝਾਕਣ ਦਿੱਤਾ।\nTRANSLATION:\n[STANZA 1] A soiled blanket that often covered me, I found myself in it, tracing paths within its folds.\n[STANZA 2] Scars of many wounds were hidden in that blanket, sometimes it comforted me, sometimes it made me weep.\n[STANZA 3] My journey was within that blanket, my weariness within it, a soiled blanket that let me peer into stories untold.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "lost",
          "loss_note": "Chadar maili (soiled blanket) is the title and central metaphor of Rajinder Singh Bedi's landmark Punjabi novel about a widow forced into levirate marriage — the symbol of the widow's compromised dignity is reduced to a generic existential metaphor, erasing the feminist literary tradition behind it.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "grief",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 3,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "The Punjabi 'kahaniyan vich jhakkan' (peering into stories) invokes the oral kissa tradition — the chadar as the site of community storytelling — entirely absent.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "ਚਾਦਰ ਮੈਲੀ",
          "romanization": "Chadar Maili",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Soiled blanket — the iconic symbol of Bedi's feminist novel, stripped of its literary and social meaning."
        }
      ]
    }
  }
]
""")
