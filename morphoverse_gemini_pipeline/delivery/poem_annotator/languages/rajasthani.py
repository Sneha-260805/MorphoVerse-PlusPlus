"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Rajasthani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: म्हारी क़दानी ज़िंदगी, महलों में, नैणां री सासां सुख पाई\nTRANSLATION: My ancestral life, in palaces, the breaths of eyes found bliss",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "pride",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "Khandani (lineage) loses Rajput nobility and generational honor connotation.",
          "metaphor_spans": [
            {
              "source_term": "नैणां री सासां",
              "abstract_meaning": "moments of perception as the breaths of the eyes – intimate, soulful awareness of ancestral bliss"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "महलों",
          "romanization": "mahlon",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Palaces as markers of Rajput heritage retained, though the specific Rajput cultural space connotation is weakened."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Rajasthani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: रंगीलो राजस्थान, पधारो म्हारे देश, थार में खुशीयां सांचो बारां\nTRANSLATION: Colorful Rajasthan, come to my land, in Thar happiness is never far",
    "output": {
      "recitation_style": "celebratory",
      "emotional_arc": "joy",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "रंगीलो",
              "abstract_meaning": "vibrancy as the essence of Rajasthani identity, turning even the desert into a canvas of color"
            },
            {
              "source_term": "खुशीयां सांचो बारां",
              "abstract_meaning": "happiness is always near – the Thar as a place of perpetual welcome and abundance"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "राजस्थान",
          "romanization": "Rajasthan",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "थार",
          "romanization": "Thar",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Rajasthani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: थार री रीती, राजीव रै रा अंगनां में, मिट्टी रो रंग, नित्य जिवन थारां में सजग\nTRANSLATION: The tradition of Thar, in Rajeev's courtyard, the color of earth, daily life adorned with grace",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "reverence",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "'Reeti' (custom) and 'Rajeev' (possibly a genealogical figure or beloved) lose their cultural specificity.",
          "metaphor_spans": [
            {
              "source_term": "मिट्टी रो रंग",
              "abstract_meaning": "the hue of the earth as the humble, mortal essence of existence and return to origin"
            },
            {
              "source_term": "सजग",
              "abstract_meaning": "awakened grace in daily acts / sacrality of mundane life"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "थार",
          "romanization": "Thar",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Desert as spiritual ground flattened."
        },
        {
          "term": "रीती",
          "romanization": "reeti",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Traditional custom lost."
        },
        {
          "term": "अंगनां",
          "romanization": "angna",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Courtyard's domestic sacredness lost; rendered as generic space."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Rajasthani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: मीरां के प्रभु गिरिधर नागर, चरण कमल बलिहारी\nTRANSLATION: Meera's Lord, Giridhar Nagar, I am devoted to your lotus feet",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Giridhar Nagar (Krishna who lifted Govardhan) loses its specific mythological weight.",
          "metaphor_spans": [
            {
              "source_term": "चरण कमल",
              "abstract_meaning": "lotus feet as the ultimate refuge and object of the devotee's complete surrender"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "मीरां",
          "romanization": "Meera",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "गिरिधर नागर",
          "romanization": "Giridhar Nagar",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Epithet flattened to generic Lord; Govardhan‑lifting miracle erased."
        }
      ]
    }
  }
]
""")
