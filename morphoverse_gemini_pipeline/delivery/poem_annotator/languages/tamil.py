"""Data-only language module (auto-migrated). Edit EXAMPLES below.
Exposes: EXAMPLES (list of {input, output}), LANGUAGE_NOTE (str).
Grounded examples only.
"""
import json

LANGUAGE_NOTE = ""

EXAMPLES = json.loads(r"""
[
  {
    "input": "LANGUAGE: Tamil\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு.\nTRANSLATION: \"A\" is the first of all letters, the primordial Lord is the first in the world.",
    "output": {
      "recitation_style": "devotional",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "lost",
          "loss_note": "The Tamil 'akara' is not merely the letter A but the primordial syllable of creation in Tamil grammatical‑cosmological tradition; the opening kural of the Thirukkural, a 2000‑year‑old ethical‑philosophical canon revered by all Tamils, is stripped of its status as a civilisational touchstone.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "அகர",
          "romanization": "akara",
          "category": "DEVOTIONAL_CONCEPT",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'A' — loses the Tamil grammatical‑cosmological tradition where akara is the first sacred sound of creation."
        },
        {
          "term": "ஆதி பகவன்",
          "romanization": "Adi Bhagavan",
          "category": "DEITY",
          "stanza_index": 1,
          "preserved": false,
          "translation_note": "Rendered as 'primordial Lord' — loses the Shaiva Siddhanta specificity of the uncaused first cause in Tamil theology."
        }
      ]
    }
  },
  {
    "input": "LANGUAGE: Tamil\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: கண்ணே களிமணே, கன்னியே, பொண்ணே பொன்னாதக் குழந்தை, பாலகமுது சுகம் தரும் மதி மாலையே, பறவைகளின் குரல் சொல்லும் மதியம் அன்றென்று நினை\nTranslation: O beautiful‑eyed girl, golden child, beloved one, you are the nectar of happiness, your voice a bird's song in the afternoon, in memories past, I weep.",
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
    "input": "LANGUAGE: Tamil\nSTANZA_COUNT: 2\nSTANZAS:\n[STANZA 1]\nSOURCE: எண்ணும் இசைமயமாக் கம்பனெழுதின மண்ணே யொன்றும் சேராதே.\n[STANZA 2]\nSOURCE: நண்ணும் வரவான கங்கை பட்டுயர்தருமென்றே.\nTRANSLATION:\n[STANZA 1] Kambar wrote in music's sweet rhythm, yet, none on this earth shall unite.\n[STANZA 2] The Ganges, in its essence, will not dwell in the land of delight.",
    "output": {
      "recitation_style": "reflective",
      "emotional_arc": "devotion",
      "stanzas": [
        {
          "index": 1,
          "emotion": "devotion",
          "tone": "wonder",
          "translation_quality": "partial",
          "loss_note": "இசைமயம் (isaimayam) refers specifically to the musical metre of Kamban's Ramayana, considered the pinnacle of classical Tamil prosody; 'music's sweet rhythm' partially preserves the musical quality but loses the technical literary‑historical achievement.",
          "metaphor_spans": []
        },
        {
          "index": 2,
          "emotion": "devotion",
          "tone": "prayer",
          "translation_quality": "partial",
          "loss_note": "The Ganga in Tamil poetry often serves as a contrast to the Kaveri, marking the boundary between Sanskritic and Tamil sacred geography; 'the Ganges, in its essence' abstracts this tension.",
          "metaphor_spans": []
        }
      ],
      "cultural_entities": [
        {
          "term": "கங்கை",
          "romanization": "Ganga",
          "category": "SACRED_RIVER",
          "stanza_index": 2,
          "preserved": true,
          "translation_note": "Sacred river retained, but its literary‑geographical resonance with Kaveri lost."
        }
      ]
    }
  }
]
""")
