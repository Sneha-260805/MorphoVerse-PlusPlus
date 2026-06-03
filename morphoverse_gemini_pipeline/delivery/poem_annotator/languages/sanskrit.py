"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Sanskrit\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: यदा यदा हि धर्मस्य ग्लानिर्भवति भारत। अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥\nTRANSLATION: Whenever there is a decline of righteousness and rise of unrighteousness, O Bharata, then I manifest Myself.\n[STANZA 2]\nSOURCE: परित्राणाय साधूनां विनाशाय च दुष्कृताम्। धर्मसंस्थापनार्थाय सम्भवामि युगे युगे॥\nTRANSLATION: For the protection of the good, for the destruction of the wicked, and for the establishment of dharma, I am born in age after age.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "declaration → declaration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "resilience",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "'धर्मस्य ग्लानि' (decline of dharma) is a cosmic soteriological concept specific to the Bhagavad‑Gita's theophany; 'decline of righteousness' approximates it but loses the technical weight of dharma as cosmic order.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "resilience",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "'धर्मसंस्थापनार्थाय' (for the establishment of dharma) carries the full authority of the divine avatāra; the translation's 'establishment of dharma' is accurate but flattens the multi‑layered meaning of dharma as law, duty, and cosmic order.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "धर्म",
          "romanization": "dharma",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Dharma as cosmic law/goodness is simplified to 'righteousness', losing its multivalence."
        },
        {
          "term": "भारत",
          "romanization": "Bharata",
          "category": "MYTHOLOGICAL_EVENT",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "युगे युगे",
          "romanization": "yuge yuge",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 2,
          "preserved": false,
          "translation_note": "The cyclic cosmic ages (yugas) are central to Hindu cosmology; 'age after age' captures the repetition but not the specific Puranic framework."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Sanskrit\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: नवीनमेघश्यामलं नभो विभाति निर्मलम्। मयूराः नृत्यन्ति हर्षिता मत्तकोकिलाः॥\nTRANSLATION: The sky shines clear, dark as a fresh raincloud. Peacocks dance joyfully, cuckoos intoxicated.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "wonder",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "नवीनमेघश्यामलं",
              "abstract_meaning": "sky as dark as a fresh raincloud – an image of purity and promise of rain"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  }
]
""")
