"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Hindi\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: श्री रामचंद्र कृपालु भजु मन हरण भव भय दारुणं।\nTRANSLATION: O mind, sing the praises of compassionate Lord Ram,\n[STANZA 2]\nSOURCE: कन्दर्प अगणित अमित छवि नव नील नीरद सुन्दरं।\nTRANSLATION: He is as charming as a newly formed dark cloud,",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "Bhav bhay loses samsaric terror nuance.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "devotion",
          "tone": "wonder",
          "translation_quality": "partial",
          "loss_note": "Kandarp rendered as Cupid dilutes devotional register.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "श्री रामचंद्र",
          "romanization": "Shri Ramchandra",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Lord Ram is retained, honorific Shri lost."
        },
        {
          "term": "भव भय",
          "romanization": "bhav bhay",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Samsaric fear flattened to worldly existence."
        },
        {
          "term": "कन्दर्प",
          "romanization": "kandarpa",
          "category": "DEITY",
          "stanza_index": 2,
          "preserved": true,
          "translation_note": "God of love correctly equated to Cupid."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Hindi\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: चिट्ठी आई है वतन से चिट्ठी आई है\nTRANSLATION: A letter has arrived, a letter from home has arrived\n[STANZA 2]\nSOURCE: आंखों में पानी लेकर हमने चिट्ठी खोली\nTRANSLATION: With tears in our eyes we opened the letter",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "longing → grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Bevatan loses specific exile anguish.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "grief",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "वतन",
          "romanization": "vatan",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Home loses vatan's sacred motherland weight."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Hindi\nSTANZA_COUNT: 4\nSTANZAS:\n[STANZA 1]\nSOURCE: वनवास का दर्द सहा था एक बार,\nTRANSLATION: Once the pain of exile was endured,\n[STANZA 2]\nSOURCE: वो था सीता का बेटा,\nTRANSLATION: He was Sita's son,\n[STANZA 3]\nSOURCE: पर इस बार बनवास का दर्द,\nTRANSLATION: But this time the pain of exile,\n[STANZA 4]\nSOURCE: धरती माँ ने रोकर कहा,\nTRANSLATION: Mother Earth wept and said,",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief → grief → grief → grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Vanavas loses Ramayana-specific exile weight.",
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
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 4,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Dharti Maa as living myth of Sita swallowed by earth lost.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "वनवास",
          "romanization": "vanavas",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Sacred exile flattened to generic exile."
        },
        {
          "term": "सीता",
          "romanization": "Sita",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "धरती माँ",
          "romanization": "Dharti Maa",
          "category": "MYTHOLOGICAL_EVENT",
          "stanza_index": 4,
          "preserved": false,
          "translation_note": "Mother Earth reduced to generic metaphor; Ramayana event erased."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Hindi\nSTANZA_COUNT: 3\nSTANZAS:\n[STANZA 1]\nSOURCE: सांझ के रंगों में डूबा,\nTRANSLATION: Drenched in the hues of evening,\n[STANZA 2]\nSOURCE: आसमान के आँचल तले,\nTRANSLATION: Beneath the sky's vast embrace,\n[STANZA 3]\nSOURCE: यह गीत सांझ का है,\nTRANSLATION: This is the song of the evening,",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "wonder",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "सांझ के रंगों में डूबा",
              "abstract_meaning": "being immersed in the sensory richness of evening"
            }
          ]
        },
        {
          "index": 2,
          "emotion": "peace",
          "tone": "wonder",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "आसमान के आँचल तले",
              "abstract_meaning": "sky as a protective maternal canopy"
            }
          ]
        },
        {
          "index": 3,
          "emotion": "peace",
          "tone": "tenderness",
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
