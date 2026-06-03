"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Urdu\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: تم آئے ہو، نور آیا ہے، ان خوابوں کا گاؤں چاندنی میں نہایا ہے، جو رات سے پیارے ہیں، جو دن سے سنہرے ہیں، وہ خواب دکھاؤ، تم آئے ہو، نور آیا ہے\nTRANSLATION: You have come, light has arrived, the village of dreams is bathed in moonlight. More beautiful than the night, brighter than the day, show me those dreams. You have come, light has arrived.",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "نور",
          "romanization": "Noor",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Urdu\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: یہ دھواں سا کہاں سے اٹھتا ہے؟ دل کے جلنے کا کچھ اثر ہے کیا؟\nTRANSLATION: Where does this smoky feeling rise from? Is it the sign of a burning heart?",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "whisper",
          "translation_quality": "partial",
          "loss_note": "دھواں (dhuan, smoke) in the Urdu ghazal tradition is the visible trace of the burning heart — a Sufi image of love's annihilation (fana). 'Smoky feeling' domesticates this into a generic emotional register.",
          "metaphor_spans": [
            {
              "source_term": "دل کے جلنے",
              "abstract_meaning": "the heart's burning as the lover's spiritual station on the path to fana (annihilation in divine love)"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "دھواں",
          "romanization": "dhuan",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Sufi image of love's annihilation flattened to 'smoky feeling'."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Urdu\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: مجھ سے پہلی سی محبت مرے محبوب نہ مانگ، میں نے سمجھا تھا کہ تو ہے تو درخشاں ہے حیات، تیرا غم ہے تو غمِ دہر کا جھگڑا کیا ہے، تیری صورت سے ہے عالم میں بہاروں کو ثبات\nTRANSLATION: Do not ask of me, my love, that love I once had for you. There was a time when life was bright, because you were what I wanted above all else, or so I thought. Your sorrow was mine, and so was the world's anguish.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "declaration",
          "translation_quality": "lost",
          "loss_note": "غمِ دہر (gham‑e‑dehr, the sorrow of the age/world) is the Urdu progressive literary term for collective historical suffering under colonial and class oppression — the pivot from romantic love to political consciousness that is this poem's entire meaning. 'The world's anguish' erases the specific Progressive Writers' Movement register. بہاروں کو ثبات (permanence to the springs) invokes the Urdu metaphor of bahar as political renaissance — lost entirely.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "غمِ دہر",
          "romanization": "gham‑e‑dehr",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Progressive term for collective historical suffering flattened to 'world's anguish'."
        },
        {
          "term": "بہاروں کو ثبات",
          "romanization": "baharon ko sabat",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Political metaphor of spring as revolutionary renaissance — omitted entirely."
        }
      ]
    }
  }
]
""")
