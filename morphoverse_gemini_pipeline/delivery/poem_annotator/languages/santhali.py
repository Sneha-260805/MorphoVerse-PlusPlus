"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Santhali\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: संताल, ज़मीन, आज़ादी\nTRANSLATION: Santhal, land, freedom\n[STANZA 2]\nSOURCE: संताल की आवाज़, गूंजेगी सदा\nTRANSLATION: The voice of the Santhal, will echo forever",
    "output": {
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
            {
              "source_term": "ज़मीन",
              "abstract_meaning": "ancestral land as the very identity of the Santhal people, not just territory"
            }
          ]
        },
        {
          "index": 2,
          "emotion": "anger",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "Gūnjegi sadā loses the tribal oral echo and the communal voice of resistance.",
          "metaphor_spans": [
            {
              "source_term": "गूंजेगी सदा",
              "abstract_meaning": "eternal resonance of the collective voice, a promise of undying memory"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "संताल",
          "romanization": "Santhal",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "ज़मीन",
          "romanization": "zameen",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Land reduced to generic; tribal ancestral territory meaning lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Santhali\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: डालखाता, नदी की लहरों में, चंचल जल की धारा, सपने सजाए ले जाता\nTRANSLATION: The fisherman, in the river waves, the playful stream carries dreams adorned",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Dalkhata is a specific folk archetype; 'fisherman' loses the cultural identity.",
          "metaphor_spans": [
            {
              "source_term": "चंचल जल की धारा",
              "abstract_meaning": "the playful stream as a carrier of fragile hopes and aspirations"
            },
            {
              "source_term": "सपने सजाए",
              "abstract_meaning": "dreams adorned and gently carried away by life's currents"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "डालखाता",
          "romanization": "Dalkhata",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Specific Santhali folk archetype lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Santhali\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: जितना पहाड़, उतना अडिग संकल्प, हाथ में हाथ हो\nTRANSLATION: As big as the mountain, that firm the resolve, hand in hand",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "resilience",
      "stanzas": [
        {
          "index": 1,
          "emotion": "resilience",
          "tone": "declaration",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "पहाड़",
              "abstract_meaning": "obstacle proportionate to the strength of collective will"
            },
            {
              "source_term": "हाथ में हाथ",
              "abstract_meaning": "solidarity as the foundation of overcoming – hands joined represent unbreakable community"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Santhali\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: मारङ बुरु देवता, जोहार, सोहराय गीत\nTRANSLATION: Marang Buru deity, greetings, Sohrai song",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "reverence",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Marang Buru loses status as supreme mountain deity; Sohrai festival context missing.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "मारङ बुरु",
          "romanization": "Marang Buru",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Supreme Santhali mountain spirit reduced to generic deity."
        },
        {
          "term": "सोहराय",
          "romanization": "Sohrai",
          "category": "FESTIVAL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Harvest festival removed; renders song generic."
        }
      ]
    }
  }
]
""")
