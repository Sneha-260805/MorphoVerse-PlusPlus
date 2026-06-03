"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Kannada\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ಗಂಗಾ, ನಿನ್ನ ನದಿಯ ಹರಿವಿನಲ್ಲಿ\nTRANSLATION: Ganga, in the flow of your river",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Ganga retains sacredness, but Virashaiva immediacy lost.",
          "metaphor_spans": [
            {
              "source_term": "ನಿನ್ನ ನದಿಯ ಹರಿವಿನಲ್ಲಿ",
              "abstract_meaning": "immersion in sacred flow / surrender to divine rhythm"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ಗಂಗಾ",
          "romanization": "Ganga",
          "category": "SACRED_RIVER",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Kannada\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ನಡೆಯ ದಾರಿಯಲ್ಲಿ ನಿನ್ನೆ ನಾಳೆಯ ನೆನಪು\nTRANSLATION: On the path of journey, memories of yesterday and tomorrow",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "whisper",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "ನಿನ್ನೆ ನಾಳೆಯ ನೆನಪು",
              "abstract_meaning": "consciousness spanning time, memory holding both past and future"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Kannada\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ನಾಡಿನ ಸಿರಿತನ ಕನಸುಗಳ ನಗು ಬಾಳದಲಿ ಬೆಳಕು\nTRANSLATION: The wealth of the land, the smile of dreams, light in life",
    "output": {
      "recitation_style": "celebratory",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "Siritana (splendor) loses specific Kannada cultural richness.",
          "metaphor_spans": [
            {
              "source_term": "ಕನಸುಗಳ ನಗು",
              "abstract_meaning": "joy of aspiration / vitality of hope"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ಸಿರಿತನ",
          "romanization": "siritana",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Splendor loses specific Kannada cultural connotation."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Kannada\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ಅವನ ನೆನಪಿಗೆ ನಮನ\nTRANSLATION: A salute to his memory",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  }
]
""")
