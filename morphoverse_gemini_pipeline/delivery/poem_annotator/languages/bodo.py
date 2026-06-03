"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Bodo\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: बोडो ग्वसिंग, तुमार धुन, संगीत भरी गुथा, मोर मनत ठोर ठोर, सपना गितार उठी।\nTRANSLATION: Bodo Gwsing, your tune woven with music, in my heart, every beat, dreams rise like melodies.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "tenderness",
          "translation_quality": "lost",
          "loss_note": "ग्वसिंग (Gwsing) is the traditional Bodo oral musical form tied to the Bwisagu festival and ancestral rites; rendered as a generic 'song', it loses its ritual identity entirely. गुथा (githa/woven) invokes the Bodo tradition of weaving dokhona fabric as cultural continuity — lost in the generic 'woven with music'.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "ग्वसिंग",
          "romanization": "Gwsing",
          "category": "MUSICAL_TRADITION",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'song' — loses the specific Bodo oral musical tradition associated with ancestral rites and the Bwisagu spring festival."
        },
        {
          "term": "गुथा",
          "romanization": "Githa",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'woven' — loses the dokhona weaving tradition that is the primary symbol of Bodo cultural identity for women."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Bodo\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ग्वसिंग ग्वरण, तुमार धुन, आत्मा, सृष्टि, मोर चित्त, मोर हृदयले शांति, जीवन गुथा।\nTRANSLATION: Song of the soul, your melody, spirit, creation, in my mind, in my heart, there's peace woven into life.",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "ग्वरण (gwron) refers specifically to the Bodo bathou cosmological concept of divine breath animating creation — translating it as 'soul' loses the bathou framework where spirit and nature are inseparable.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "ग्वसिंग ग्वरण",
          "romanization": "Gwsing Gwrwn",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'Song of the Soul' — Gwrwn is the bathou concept of divine breath, not a generic soul; the translation removes the Bodo animist cosmology."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Bodo\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: न्वज्व ब्विसागु, तुमार स्वागत, नতুন, স্বপ্ন, मोर হৃদय, जीवनले गुथा, सपना गितार।\nTRANSLATION: New beginnings, your welcome, new, dreams, in my heart, woven into life, a melody of dreams.",
    "output": {
      "recitation_style": "celebratory",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "declaration",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "ब्विसागु",
          "romanization": "Bwisagu",
          "category": "FESTIVAL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  }
]
""")
