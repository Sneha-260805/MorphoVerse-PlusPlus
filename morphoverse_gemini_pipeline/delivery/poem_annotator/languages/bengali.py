"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Bengali\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: তোমার বিনা আমার দিন কাটে\nএকা একা আলো ছাড়া।\nতোমার বিনা জীবনের পথে\nযায় এক শূন্যতা।\nTRANSLATION: Without you, my days pass\nAlone, without light.\nWithout you, on the path of life,\nThere walks an emptiness.",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Bengali\nSTANZA_COUNT: 4\nSTANZAS:\n[STANZA 1]\nSOURCE: ও আমার দেশের মাটি,\nতোমার কল্যাণে চাহি,\nপ্রাণে প্রাণে মিলে যেতে,\nগানের সুরে চাহি।\n[STANZA 2]\nSOURCE: স্নেহের বৃষ্টি নামে,\nবৃষ্টি মাথার উপর।\nজীবনের পথ চলে,\nশান্তির আলো তোলে।\n[STANZA 3]\nSOURCE: সৃষ্টির খোঁজে যাই,\nতুমি আমার শিকড়।\nদেশের মাটির সুরে,\nপেতে চাই তোমার টান।\n[STANZA 4]\nSOURCE: ও আমার দেশের মাটি,\nঅশ্রুর নদী flows,\nমা তুমি, মাটি তুমি,\nসুখে থাকুক সারা জীবন।\nTRANSLATION:\n[STANZA 1] O soil of my country, In your welfare, I seek, To blend together in life, In the melody of songs.\n[STANZA 2] The rains of affection fall, Raining upon my head. The path of life travels, Bringing forth the light of peace.\n[STANZA 3] I go in search of creation, You are my roots. In the tune of the soil, I long for your embrace.\n[STANZA 4] O soil of my country, The river of tears flows, Mother, you are the land, May you be happy all your life.",
    "output": {
      "recitation_style": "declarative",
      "emotional_arc": "longing → peace → longing → grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "declaration",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "peace",
          "tone": "tenderness",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 3,
          "emotion": "longing",
          "tone": "prayer",
          "translation_quality": "faithful",
          "loss_note": "",
          "metaphor_spans": []
        },
        {
          "index": 4,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "partial",
          "loss_note": "The mixed-language line 'অশ্রুর নদী flows' (Bengali noun + English verb) is a deliberate poetic device signalling cultural rupture — the translation normalises it to plain English, erasing this formal signal of displacement.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Bengali\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: যেতে যেতে দেখেছি\nঅদৃশ্য পথিকের কাছে এসে\nমোর মনের নিকট,\nআমি মৃদু মৃদু মনে মনে বলি।\nএকা একা চলতে গিয়ে\nকত যে কথা বলি।\nTRANSLATION: While going, I have seen\nComing near the invisible traveler\nTo my heart,\nI softly speak in my mind.\nWalking alone,\nHow many words I share.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "longing",
      "stanzas": [
        {
          "index": 1,
          "emotion": "longing",
          "tone": "whisper",
          "translation_quality": "lost",
          "loss_note": "অদৃশ্য পথিক (the invisible traveller) is a trope with deep roots in Baul and Sahajiya mystical poetry — the unseen divine companion walking alongside the soul. The translation renders it as a generic 'invisible traveler', with no mystical register, losing the entire Baul-Sahajiya devotional dimension.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": []
    }
  }
]
""")
