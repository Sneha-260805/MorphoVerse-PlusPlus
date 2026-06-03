"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Konkani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: डाखलो साल्ट, संपूर्ण जगात सोडून देतं, जीवन स्वाद आणता\nTRANSLATION: A pinch of salt, leaving everything behind in the whole world, it brings flavor to life",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Dakhlo, a uniquely Konkani expression for 'a pinch', loses its culinary‑folk minimalism.",
          "metaphor_spans": [
            {
              "source_term": "डाखलो साल्ट",
              "abstract_meaning": "insignificant self that paradoxically seasons the whole of existence with meaning"
            },
            {
              "source_term": "सोडून देतं",
              "abstract_meaning": "renunciation of attachment / letting go of the ego in the vastness of the world"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "डाखलो",
          "romanization": "dakhlo",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Local phrase for 'a pinch' lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Konkani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: झली व्हालं आला, संपूर्ण आकाशाचं गौरव करून, प्रत्येक फुशीत तुला प्रिय करतो\nTRANSLATION: The lover came, honoring the entire sky, in every whisper I cherish you",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Zhali vhalan's folk intimacy and the Goan romantic register diluted.",
          "metaphor_spans": [
            {
              "source_term": "आकाशाचं गौरव",
              "abstract_meaning": "beloved's presence elevates the cosmos to celestial significance"
            },
            {
              "source_term": "प्रत्येक फुशीत",
              "abstract_meaning": "tenderness communicated in the smallest breath / love in every whisper"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "फुशी",
          "romanization": "phushi",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Whisper as intimate Konkani communication lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Konkani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: देव बोरें आम्हां, जिवंत ठेवील, संपूर्ण आकाशात उगवलेली आशा\nTRANSLATION: God will save us, keep us alive, hope rising in the vast sky",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Amhan ('us') carries the weight of Konkani diaspora and minority community; collective identity weakened.",
          "metaphor_spans": [
            {
              "source_term": "जिवंत ठेवील",
              "abstract_meaning": "divine life‑sustenance / grace as survival"
            },
            {
              "source_term": "आकाशात उगवलेली आशा",
              "abstract_meaning": "hope ascending to heaven / prayer rising like dawn"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "देव",
          "romanization": "dev",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "God retained, but the specific Catholic or Hindu identity ambiguous."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Konkani\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: पावसाचे राती, मांडवाच्या सावळी, सोबित कान्तार गायतात\nTRANSLATION: On rainy nights, in the shade of the mandó, they sing beautiful songs",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Mandó is a specific Goan song form, a cultural institution; 'shade of the mandó' obscures this.",
          "metaphor_spans": [
            {
              "source_term": "मांडवाच्या सावळी",
              "abstract_meaning": "the mandó gathering as a shelter for the soul, where music becomes a communal refuge"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "कान्तार",
          "romanization": "kantar",
          "category": "MUSICAL_TRADITION",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Folk song rendered generic."
        }
      ]
    }
  }
]
""")
