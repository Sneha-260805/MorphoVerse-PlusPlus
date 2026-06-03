"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Marathi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: जीवनाच्या काठावर ताठ बसलेली, दररोज माझ्या स्वप्नांच्या तळाशी ती उभी आहे.\nTRANSLATION: Sitting upright at the edge of life, every day she stands at the depths of my dreams.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Marathi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: माझ्या हृदयाच्या गाभ्यात, माझ्या आतल्या कवितेत, संपूर्ण जगणं समेटीत आहे, मरणाचं गाणं गातो.\nTRANSLATION: In the core of my heart, in the depths of my poetry, life converges completely, I sing the song of death.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "मरणाचं गाणं (the song of death) in the Varkari‑influenced Marathi tradition carries an acceptance of death as liberation — marana as moksha — that is qualitatively different from the English 'song of death', which reads as morbid rather than as spiritual surrender.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "मरण",
          "romanization": "marana",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "In Varkari Marathi tradition, marana (death) is embraced as liberation and union with Vitthal; 'death' in English lacks this soteriological register."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Marathi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: जगण्याच्या उंबरठ्यावर नकोशी जन्मली, उजाडून गेलेला तो काळोख सर्वत्र नाचत राहतोय.\nTRANSLATION: Born at the threshold of life, the darkness that dawned keeps dancing everywhere.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "lost",
          "loss_note": "The word Nakoshi — the Marathi term for unwanted girl children historically given this name to express parental rejection — is entirely absent from the translation, which loses the poem's entire subject and social critique, reducing it to a generic grief poem.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "नकोशी",
          "romanization": "Nakoshi",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Nakoshi is a documented Maharashtrian social practice of naming unwanted girl children 'don't want her' to express rejection at birth. The translation omits the word entirely, erasing the poem's social critique."
        }
      ]
    }
  }
]
""")
