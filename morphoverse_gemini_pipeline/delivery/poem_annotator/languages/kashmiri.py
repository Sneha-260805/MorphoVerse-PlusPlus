"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Kashmiri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: وٛچھُم یار گچٕن، کھر منزٕ لُٹ ہند ہار گچٕن، برکھہ تُتھ ؤچھ بوٚن منزٕ بیہٕس، وٛچھُم یار گچٕن۔\nTRANSLATION: I saw my lover leave, leaving behind the home adorned with pearls. The rain fell, and I sat under a tree, I saw my lover leave.",
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
    "input": "LANGUAGE: Kashmiri\nSTANZA_COUNT: 3\nSTANZAS:\n[STANZA 1]\nSOURCE: کشمیر، کی چھٕ پوٚست آفِس راتی گٕلٕوٚن گٕچھٕ؟ چھٕس یٲتٕھ ہند کھیسِت پٲٹھ اور موسمٕ آوٚن چھٕنٕ۔\n[STANZA 2]\nSOURCE: میہٕ ژٔند ہٕندٕ ٹُھریٚ ہر پتھر چھٕ یِک زٲندَک ہند گھرانی چھٕں ٹُرٕن دیٔندٕ بچٕو چھٕں ہنوز وٛچھیٚن۔\n[STANZA 3]\nSOURCE: مٕنٕس کی زٲند زِندٕرٕ جہاں خاموشی راستۂ سٕرۂِ جہاں سورج سُنٛن نہ کرن اور سایے بےخبر پھلٕن۔\nTRANSLATION:\n[STANZA 1] Kashmir, is there a post office, for letters arriving at dusk? We are waiting to be told the history of snow and learn the names of seasons.\n[STANZA 2] My world is in fragments, each shard reflects a life, of families torn by the wind, of children who still wait to be found.\n[STANZA 3] Let me speak to you of the valley, where silence moves through the streets, where the sun sets without a sound, and shadows fall unnoticed.",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "whisper",
          "translation_quality": "partial",
          "loss_note": "The Kashmiri word for snow (sheen) carries layered weight of the conflict — snow as witness, snow as the period of enforced silence during curfew, snow as burial. 'History of snow' partially preserves this but misses the specific post‑1989 political resonance.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "grief",
          "tone": "lament",
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
        }
      ],
      "cultural_entities": []
    }
  },
  {
    "input": "LANGUAGE: Kashmiri\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: چُھ دھوٚنٕ زٕر زٕندٕ، چٕھ نٕزٕر کھیٚؤنٕ، زٕندٕ یا کُنجَرٕ، سُرٕ وٚسٕنٕ کُت بٕرٛچھٕ۔\nTRANSLATION: It flows through life, an essence of existence, in every heartbeat, the soul whispers through veins.",
    "output": {
      "recitation_style": "lament",
      "emotional_arc": "grief",
      "stanzas": [
        {
          "index": 1,
          "emotion": "grief",
          "tone": "lament",
          "translation_quality": "lost",
          "loss_note": "خونی (khouni/blood) in post‑conflict Kashmiri poetry is a politically charged term invoking the bloodshed of the insurgency years, not a philosophical meditation on blood‑as‑life. The word kunjara (dark hidden alley, a site of disappearance) is omitted entirely from the translation, erasing the poem's spatial politics.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "کُنجَرٕ",
          "romanization": "kunjara",
          "category": "REGIONAL_SYMBOL",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Dark hidden alley, a site of disappearance in conflict‑era Kashmiri poetry; not translated at all, erasing the poem's spatial politics."
        }
      ]
    }
  }
]
""")
