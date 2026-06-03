"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Gujarati\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: मारा प्राणाद, सदा संग छे, जीवन ना हर एक रंग छे। आँखो मा सपना, दिल मा उमंग, जीवन ना हर एक रंग छे।\nTRANSLATION: My life, always with me, every color of life. In my eyes, dreams, in my heart, enthusiasm, every color of life.",
    "output": {
      "recitation_style": "celebratory",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "declaration",
          "translation_quality": "partial",
          "loss_note": "प्राणाद (pranad) is not merely 'life' but the Sanskrit‑rooted Gujarati concept of life as prana — the vital breath that is the animating principle in Vaishnava philosophy; translating it as 'my life' collapses a theological concept into a personal one. उमंग (umang) rendered as 'enthusiasm' loses the specifically Gujarati devotional register where umang is the upsurge of bhakti joy, not secular excitement.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "प्राणाद",
          "romanization": "Pranad",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'life' — loses the prana/vital-force theology of the Vaishnava-Gujarati tradition rooted in Narsinh Mehta's bhakti framework."
        },
        {
          "term": "उमंग",
          "romanization": "Umang",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'enthusiasm' — loses the devotional bhakti-joy register specific to Gujarati Vaishnava poetry."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Gujarati\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: सूरज ऊगे છે, થોડો અજવાળો લાવે છે, ફૂલો ખીલે છે, થોડી મહેક આપે છે.\nTRANSLATION: The sun rises, brings a little light; flowers bloom, give a little fragrance.",
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
  }
]
""")
