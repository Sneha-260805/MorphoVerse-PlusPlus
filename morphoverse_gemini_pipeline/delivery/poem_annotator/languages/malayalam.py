"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Malayalam\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: പഴയ ചുരുളിൽ ചന്ദനം, അവശേഷിച്ച വാസന, ഓർമ്മകളിൽ പുകഞ്ഞു വരുന്നു\nTRANSLATION: Sandalwood in the old scroll, the lingering scent, smoldering through my memories",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Chandhanam loses its sacred ritual and spice‑trade associations; 'sandalwood' is generic.",
          "metaphor_spans": [
            {
              "source_term": "ചന്ദനം",
              "abstract_meaning": "sacred fragrance as the trace of a hallowed past / spiritual essence fading"
            },
            {
              "source_term": "ഓർമ്മകളിൽ പുകഞ്ഞു",
              "abstract_meaning": "memory as a slow, smoky burning – the past continuously re‑emerging into consciousness"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ചന്ദനം",
          "romanization": "chandhanam",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Sandalwood’s religious and historical depth lost."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Malayalam\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: കുട്ടികൃഷ്ണ മാരാർ, ആലോചനയുടെ ആഴത്തിൽ, ചിന്തകൾ പൂക്കുന്ന\nTRANSLATION: Kuttikrishna Marar, in the depths of thought, ideas bloom",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Kuttikrishna Marar is a 14th‑century Vaishnavite poet‑philosopher; identity lost to English readers.",
          "metaphor_spans": [
            {
              "source_term": "ആലോചനയുടെ ആഴത്തിൽ",
              "abstract_meaning": "immersion into the ocean of philosophical contemplation"
            },
            {
              "source_term": "ചിന്തകൾ പൂക്കുന്ന",
              "abstract_meaning": "intellectual blooming / wisdom emerging naturally"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Malayalam\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: എന്റെ ജീവിതത്തിന്റെ വഴി, അവസാനം തേടുന്നു, സൂക്ഷ്മബോധം തുടരുന്നു\nTRANSLATION: The path of my life, seeking the end, subtle intuition follows",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "peace",
      "stanzas": [
        {
          "index": 1,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Kaaladi (homonym for 'path' and Shankara's birthplace) collapses to generic 'path'.",
          "metaphor_spans": [
            {
              "source_term": "വഴി",
              "abstract_meaning": "life as a journey toward its own resolution"
            },
            {
              "source_term": "സൂക്ഷ്മബോധം",
              "abstract_meaning": "subtle inner knowing, beyond rational thought, that guides the soul"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Malayalam\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: മഴ പെയ്യുന്നു, വഞ്ചിയിൽ ഇരുന്നു, പെരിയാറിന്റെ ഓളങ്ങളിൽ\nTRANSLATION: Rain is falling, sitting in the boat, on the waves of the Periyar",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "lament",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "മഴ",
              "abstract_meaning": "monsoon as both emotional release and the life‑giving pulse of Kerala"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "വഞ്ചി",
          "romanization": "vanchi",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Traditional boat retained."
        }
      ]
    }
  }
]
""")
