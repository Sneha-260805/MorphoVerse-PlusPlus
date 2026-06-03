"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Odia\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ଡାଳୀ ଝିଆ, ସୂର୍ଯ୍ୟ ତଳେ\nTRANSLATION: The flower girl, under the sun",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Dali Jhia loses its folkloric, possibly ritual, feminine archetype.",
          "metaphor_spans": [
            {
              "source_term": "ଡାଳୀ ଝିଆ",
              "abstract_meaning": "embodiment of youthful natural grace and innocence"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ସୂର୍ଯ୍ୟ",
          "romanization": "Surya",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Odia\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: କଳିଙ୍ଗ ଗାଥା, ଏଠାରେ ଅନୁକ୍ରମ\nTRANSLATION: The tale of Kalinga, here unfolds a sequence\n[STANZA 2]\nSOURCE: ମାତୃକା ହୃଦୟର ରମ୍ୟା\nTRANSLATION: The beauty of the mother's heart",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace → peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "wonder",
          "translation_quality": "partial",
          "loss_note": "Kalinga reference loses historical-political weight.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Matrika reduced to generic mother, loses divine feminine principle.",
          "metaphor_spans": [
            {
              "source_term": "ମାତୃକା ହୃଦୟ",
              "abstract_meaning": "the divine maternal compassion as the source of beauty"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "କଳିଙ୍ଗ",
          "romanization": "Kalinga",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Historical Kalinga identity flattened."
        },
        {
          "term": "ମାତୃକା",
          "romanization": "Matrika",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 2,
          "preserved": false,
          "translation_note": "Divine mother principle lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Odia\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ପିପିଳି ରେ, ପିପିଳି ରେ, ତୁମେ କେଉଁ ତାଲ ଦେଖିଛ\nTRANSLATION: Pipili, oh Pipili, what rhythm do you see?",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "wonder",
          "translation_quality": "partial",
          "loss_note": "Pipili may reference the appliqué town; lost in translation.",
          "metaphor_spans": [
            {
              "source_term": "କେଉଁ ତାଲ",
              "abstract_meaning": "asking what order the beloved perceives, implying different temporal/rhythmic consciousness"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ତାଲ",
          "romanization": "tal",
          "category": "MUSICAL_TRADITION",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Rhythm as fundamental Indian musical concept partially preserved."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Odia\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ବରଷାର ଧାରା, ଶରତ ଆସିଲା\nTRANSLATION: The streams of rain, autumn has come",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "ବରଷାର ଧାରା",
              "abstract_meaning": "continuous flow of rain as the passage of time and sorrow"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ଶରତ",
          "romanization": "sharat",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Autumn has specific cultural resonance in Odia seasonal poetry."
        }
      ]
    }
  }
]
""")
