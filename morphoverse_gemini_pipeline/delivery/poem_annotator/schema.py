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

# ── Status / confidence vocabularies ─────────────────────────────────────────
STATUS_COMPLETED = "completed"
STATUS_SALVAGED = "salvaged"      # valid JSON but hallucinated terms were dropped
STATUS_FAILED = "failed"          # no valid annotation produced
STATUS_PENDING = "pending"

ALIGNMENT_OK = "aligned"
ALIGNMENT_LOW = "aligned_low"
ALIGNMENT_RISK = "alignment_risk"
