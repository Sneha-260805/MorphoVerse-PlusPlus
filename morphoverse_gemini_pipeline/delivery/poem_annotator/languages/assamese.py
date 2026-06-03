"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Assamese\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ও মুর আপোনাৰ দেশ,\nতাত শান্তি আৰু স্নেহ।\nমোৰ হৃদয়ৰ গহীনত\nমোৰ পুৰণি সপোন।\nTRANSLATION: O my native land,\nThere is peace and love there.\nIn the depths of my heart,\nLie my old dreams.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "declaration",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Assamese\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: প্ৰতিমা, তুমি এক নিবেদনে\nস্নেহৰ পবনে আহা,\nমোৰ মনৰ প্ৰতিধ্বনি,\nআকাশত বেজে ওঠা।\nTRANSLATION: Idol, you come in a dedication\nWith the breeze of affection,\nThe echo of my heart,\nResounding in the sky.",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "প্ৰতিমা (Pratima) is not merely an idol — it is a consecrated devotional image in the Vaishnavite tradition; 'idol' flattens this into a generic object, losing the act of ritual invocation embedded in the Assamese word.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "প্ৰতিমা",
          "romanization": "Pratima",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as generic 'idol', losing the specific Vaishnavite consecrated-image connotation central to Assamese devotional practice."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Assamese\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: নদী, তুঁতৰ বাণী বহে\nপ্ৰবাহিত শান্তিৰ বাটে,\nমোৰ বুকুত তোমাৰ সুৰ\nসাজে যুগে যুগে।\nTRANSLATION: O River, your voice flows\nAlong the path of peace,\nIn my heart, your melody\nPlays through the ages.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "lost",
          "loss_note": "তুঁতৰ বাণী (the voice of the mulberry) is a culturally specific Assamese image — the mulberry tree feeds the silkworm of Assam's muga silk tradition, tying the river to Assam's weaving heritage; the translation renders this as a generic 'your voice', erasing the cultural image entirely with no trace remaining.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "তুঁত",
          "romanization": "tüt",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "The mulberry tree is the foundation of Assam's muga and pat silk traditions; its presence ties the river to Assam's weaving heritage, but the translation erases this connection entirely."
        }
      ]
    }
  }
]
""")
