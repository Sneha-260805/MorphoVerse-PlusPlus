"""Canonical schema definition — the single source of truth.

Every other module (prompt builder, validator, assembler, output writer) imports
its key sets and enums from here so the schema can never drift across files.

NOTE: `visual_motifs` has been removed from the schema entirely.
"""
from __future__ import annotations

# ── Enumerated label sets ────────────────────────────────────────────────────
ALLOWED_RECITATION_STYLES = (
    "lament", "devotional", "celebratory", "reflective", "declarative",
)
ALLOWED_EMOTIONS = (
    "grief", "longing", "devotion", "peace", "celebration",
    "resilience", "anger", "fear",
)
ALLOWED_TONES = (
    "lament", "whisper", "declaration", "prayer",
    "wonder", "defiance", "tenderness",
)
ALLOWED_TRANSLATION_QUALITIES = ("faithful", "partial", "lost")
ALLOWED_ENTITY_CATEGORIES = (
    "DEITY",
    "SACRED_RIVER",
    "FESTIVAL",
    "MUSICAL_TRADITION",
    "DEVOTIONAL_CONCEPT",
    "REGIONAL_SYMBOL",
    "SOCIAL_CUSTOM",
    "MYTHOLOGICAL_EVENT",
)

# ── Exact key sets accepted from the model (no visual_motifs anywhere) ───────
TOPLEVEL_KEYS = frozenset({"recitation_style", "emotional_arc", "stanzas", "cultural_entities"})
STANZA_KEYS = frozenset({"index", "emotion", "tone", "translation_quality", "loss_note", "metaphor_spans"})
METAPHOR_KEYS = frozenset({"source_term", "abstract_meaning"})
ENTITY_KEYS = frozenset({"term", "romanization", "category", "stanza_index", "preserved", "translation_note"})

# ── MorphoVerse++ Schema v1.1 extensions ─────────────────────────────────────
SCHEMA_VERSION_V1_1 = "1.1"

ALLOWED_VISUAL_PRIORITIES = ("essential", "supporting", "optional", "non_visual")
ALLOWED_EXPRESSION_TYPES = (
    "metaphor", "simile", "idiom", "symbolism",
    "personification", "allusion", "proverb", "other",
)
ALLOWED_CULTURAL_SPECIFICITY_LEVELS = ("high", "medium", "low")
ALLOWED_VISUALIZATION_DIFFICULTY = ("easy", "moderate", "hard")

# Required v1.1 keys (pilot fields remain optional).
METAPHOR_KEYS_V1_1 = frozenset({
    "source_term", "abstract_meaning", "expression_type",
    "literal_meaning", "metaphor_mapping",
})
ENTITY_KEYS_V1_1 = frozenset({
    "term", "romanization", "category", "stanza_index", "preserved", "translation_note",
    "source_span_original", "source_span_translation",
    "visual_priority", "acceptable_visual_variants",
})
ENTITY_OPTIONAL_PILOT_KEYS = frozenset({"cultural_specificity_level", "visualization_difficulty"})
ANNOTATION_OPTIONAL_PILOT_KEYS = frozenset({"cultural_specificity_level", "visualization_difficulty"})

# ── Status / confidence vocabularies ─────────────────────────────────────────
STATUS_COMPLETED = "completed"
STATUS_SALVAGED = "salvaged"      # valid JSON but hallucinated terms were dropped
STATUS_FAILED = "failed"          # no valid annotation produced
STATUS_PENDING = "pending"

ALIGNMENT_OK = "aligned"
ALIGNMENT_LOW = "aligned_low"
ALIGNMENT_RISK = "alignment_risk"

# ── Abbreviated key maps (model outputs compact keys; pipeline expands before validation) ──
# These save ~40% output tokens and allow simple annotations to fit in the proxy's
# ~37-token completion budget.
ABBREV_TOPLEVEL = {
    "rs": "recitation_style",
    "ea": "emotional_arc",
    "st": "stanzas",
    "ce": "cultural_entities",
}
ABBREV_STANZA = {
    "i":  "index",
    "em": "emotion",
    "to": "tone",
    "tq": "translation_quality",
    "ln": "loss_note",
    "ms": "metaphor_spans",
}
ABBREV_METAPHOR = {
    "src": "source_term",
    "st":  "source_term",   # fallback: format previously showed "st" for source_term
    "am":  "abstract_meaning",
}
ABBREV_ENTITY = {
    "tm": "term",
    "rm": "romanization",
    "ct": "category",
    "si": "stanza_index",
    "pr": "preserved",
    "tn": "translation_note",
}
