"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Dogri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: मेरे पिंड दी गलां, सुन सजना, साडा रंगीला जिंदगानी, चुन्नी तले सहेजा, सपना सारे।\nTRANSLATION: Talk of my village, listen, dear, our colorful life, stored beneath the veil, all dreams together.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "पिंड (pind) in Dogri carries the weight of the Pahari village community as a living unit of shared memory — 'village' is geographically accurate but culturally thin. चुन्नी (chunni) buried with dreams is a Dogri pahadi tradition where the chunni is a repository of a woman's interior emotional world.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "पिंड",
          "romanization": "Pind",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'village' — loses the Pahari communal identity embedded in the term."
        },
        {
          "term": "चुन्नी",
          "romanization": "Chunni",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'veil' — loses the Dogri pahadi tradition of the chunni as a repository of interior emotional life."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Dogri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: चांदना दी रौशनी, पिंड दे रुत विच, सपने सजावे सजीले, रातां दी खामोशी।\nTRANSLATION: The moonlight's glow, in the village's season, adorning dreams, in the silence of the night.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
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
    "input": "LANGUAGE: Dogri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: जिंदगी दी कहाणी, उमीदां विच लिपटी, हर मोड़ ते इक नवा सपना, राह विच बणदा साथी।\nTRANSLATION: The story of life wrapped in hopes, at every turn, a new dream, a companion on the path.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "resilience",
      "stanzas": [
        {
          "index": 1,
          "emotion": "resilience",
          "tone": "declaration",
          "translation_quality": "lost",
          "loss_note": "साथी (saathi) in Dogri poetry specifically invokes the Pahari concept of a fellow traveller who shares the burden and songs of a mountain path — not a generic companion. The translation 'companion on the path' conveys direction but erases the communal mountain‑journey register entirely.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "साथी",
          "romanization": "Saathi",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'companion' — loses the Pahari oral tradition of the saathi as a fellow traveller on seasonal mountain migrations, a figure of shared communal survival."
        }
      ]
    }
  }
]
""")
