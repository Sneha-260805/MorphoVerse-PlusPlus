"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Manipuri\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: सिरिंग आहंगबा, तुमतुम्बा लोंतखा, पुमपम्ची, नचुम पांगक्ले\nTRANSLATION: Spring comes, soft and gentle frees the earth, flowers bloom, buds awake\n[STANZA 2]\nSOURCE: फुम्ना निंगं बा लैरेम, तुम्बेइबा मतंबंग रसे\nTRANSLATION: Sky's wide gentle dome, heart finds sweetest home",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "celebration → peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Siring's specific Manipuri seasonal rebirth significance lost.",
          "metaphor_spans": [
            {
              "source_term": "तुमतुम्बा लोंतखा",
              "abstract_meaning": "gentle liberation of earth from winter's grasp"
            }
          ]
        },
        {
          "index": 2,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Lairem (sky‑deity) connotation lost.",
          "metaphor_spans": [
            {
              "source_term": "तुम्बेइबा",
              "abstract_meaning": "heart finding its true dwelling in nature / spiritual homecoming"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Manipuri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: एगी निंगथेम सिरंग ईरा, हेंगु सनेगी फन्नबा मनोरा\nTRANSLATION: My beloved, a blossom in spring, a joy no other love could bring",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "सिरंग ईरा",
              "abstract_meaning": "beloved as the very essence of spring – beauty, renewal, and fragrant presence"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Manipuri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: थैना गी निनोइसीगु, लैरम थाकु थमबी ओइ, लेईफा चिंगलै फोरिंबु\nTRANSLATION: Rainy season in my heart, the sky cries tears of life, flowers bloom, leaves sway",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Thaina's dual nature as both destroyer and life‑giver – central to Manipuri monsoon culture – flattened.",
          "metaphor_spans": [
            {
              "source_term": "लैरम थाकु",
              "abstract_meaning": "sky weeping as both sorrow and sustenance for the earth"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "थैना",
          "romanization": "thaina",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Monsoon's cultural‑ecological significance muted."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Manipuri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: रास लीला, राधा कृष्ण नाचे, लोकटाक गी पानी नाचे\nTRANSLATION: Ras Leela, Radha Krishna dance, the waters of Loktak dance",
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
          "metaphor_spans": [
            {
              "source_term": "लोकटाक गी पानी नाचे",
              "abstract_meaning": "the lake itself participates in the cosmic dance of the divine lovers"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "रास लीला",
          "romanization": "Ras Leela",
          "category": "MUSICAL_TRADITION",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "राधा",
          "romanization": "Radha",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "कृष्ण",
          "romanization": "Krishna",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        },
        {
          "term": "लोकटाक",
          "romanization": "Loktak",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  }
]
""")
