"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Sindhi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: پيار جا گيت، اکيون جو پيغام، سورج جي کرڻن جهڙو\nTRANSLATION: Songs of love, the message of the eyes, like the sun's rays",
    "output": {
      "recitation_style": "celebratory",
      "emotional_arc": "celebration",
      "stanzas": [
        {
          "index": 1,
          "emotion": "celebration",
          "tone": "tenderness",
          "translation_quality": "partial",
          "loss_note": "Akhya jo payam (eyes' message) loses the non‑verbal intimacy specific to Sindhi romantic tradition.",
          "metaphor_spans": [
            {
              "source_term": "پيار جا گيت",
              "abstract_meaning": "love given voice through song / devotion made audible"
            },
            {
              "source_term": "اکيون جو پيغام",
              "abstract_meaning": "eyes as silent messengers of the soul's affection"
            }
          ]
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Sindhi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ڌرتي جيڪا تون ڏيکاريندين، سرهاڻ جو گل\nTRANSLATION: That land you show me, a garland of fragrance",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "'Dharti' is not just land but the sacred Sindhi homeland, a living presence; partition context lost.",
          "metaphor_spans": [
            {
              "source_term": "ڌرتي",
              "abstract_meaning": "homeland as the spiritual beloved, source of identity"
            },
            {
              "source_term": "سرهاڻ جو گل",
              "abstract_meaning": "offering of devotion adorned on the body / fragrance as the invisible bond of love"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ڌرتي",
          "romanization": "Dharti",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Sacred Sindhi land reduced to generic 'land'."
        },
        {
          "term": "سرهاڻ",
          "romanization": "serhano",
          "category": "SOCIAL_CUSTOM",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Garland offering custom flattened."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Sindhi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: خاموش رات ۾، دلين جا راز ڳُڻجن ٿا، اکيون رت ساڳيءَ طرح\nTRANSLATION: In the silent night, the secrets of hearts are revealed, eyes red as blood",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "Khamosh raat (silent night) has specific Sufi mystical resonance; 'silent night' flattens it.",
          "metaphor_spans": [
            {
              "source_term": "خاموش رات",
              "abstract_meaning": "sacred darkness where inner truth emerges / the Sufi's introspective hour"
            },
            {
              "source_term": "اکيون رت",
              "abstract_meaning": "weeping so profound it becomes blood / emotional exhaustion made visible"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "رات",
          "romanization": "raat",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Night as spiritual unveiling partially maintained."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Sindhi\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: ساقي، اسان کي عشق جو جام پيار، ماڪي جي مئخاني ۾\nTRANSLATION: Saqi, give us the cup of ishq, in the wine‑house of the heart",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "prayer",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": [
            {
              "source_term": "عشق جو جام",
              "abstract_meaning": "cup of divine love as intoxication of the soul / spiritual ecstasy"
            },
            {
              "source_term": "مئخاني ۾",
              "abstract_meaning": "the heart as the tavern where the divine cupbearer pours spiritual wine"
            }
          ]
        }
      ],
      "cultural_entities": [
        {
          "term": "ساقي",
          "romanization": "saqi",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": "Sufi cupbearer archetype preserved."
        },
        {
          "term": "عشق",
          "romanization": "ishq",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": true,
          "translation_note": ""
        }
      ]
    }
  }
]
""")
