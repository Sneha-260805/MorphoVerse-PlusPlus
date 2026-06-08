"""CI gate: confidence reflects FINAL annotation quality, and every review item
reaches the human-review queue.

Covers two production invariants:
  1. Confidence hard rules (assemble.confidence_label):
       - translation_fidelity_score <= 0.5 is never "high"
       - any dropped entity / metaphor / review item is never "high"
       - high only when alignment good, fidelity good, nothing dropped,
         no review items, no low-confidence stanza
  2. Human-review routing:
       - any non-empty review_items forces needs_human_review = True (assemble)
       - every review item is exported to the queue (output.build_review_rows)
       - queue row count for a poem == len(review_items)

Run:  pytest -q
"""
import pytest

from poem_annotator.assemble import confidence_label, assemble_annotation
from poem_annotator.output import build_review_rows
from poem_annotator.dataset import PreprocessedPoem, StanzaInput


# ── Helpers ───────────────────────────────────────────────────────────────────
def _clean_kwargs(**overrides):
    """A fully-clean confidence call (would be 'high') with selective overrides."""
    base = dict(
        alignment_conf=0.9,
        status="completed",
        dropped_entities=0,
        dropped_metaphors=0,
        review_items_count=0,
        translation_fidelity_score=0.8,
        low_stanza_ratio=0.0,
    )
    base.update(overrides)
    return base


def _review_item(i: int) -> dict:
    return {
        "field_path": f"annotation.stanzas[{i}]",
        "severity": "low",
        "resolved_value": "x",
        "model_value": "y",
        "note": f"note_{i}",
    }


def _poem(n_stanzas: int = 1, *, alignment_status="aligned", alignment_conf=0.9) -> PreprocessedPoem:
    stanzas = [StanzaInput(i, 1, [f"src{i}"], [f"tr{i}"]) for i in range(1, n_stanzas + 1)]
    return PreprocessedPoem(
        "P1", "Title", "Bengali", "\n".join(f"src{i}" for i in range(1, n_stanzas + 1)),
        "\n".join(f"tr{i}" for i in range(1, n_stanzas + 1)),
        stanzas, n_stanzas, n_stanzas, alignment_status, alignment_conf, "",
    )


def _gated_payload(poem: PreprocessedPoem, *, tq="faithful", loss_note="", metaphors=None, entities=None):
    return {
        "recitation_style": "reflective",
        "emotional_arc": "calm",
        "stanzas": [
            {
                "index": s.stanza_index,
                "emotion": "peace",
                "tone": "whisper",
                "translation_quality": tq,
                "loss_note": loss_note,
                "metaphor_spans": list(metaphors or []),
            }
            for s in poem.stanzas
        ],
        "cultural_entities": list(entities or []),
    }


# ── Confidence: hard rules ────────────────────────────────────────────────────
class TestConfidenceLabel:
    def test_high_requires_all_green(self):
        assert confidence_label(**_clean_kwargs()) == "high"

    def test_translation_fidelity_exactly_half_is_low(self):
        # Boundary: <= 0.5 must never be high.
        assert confidence_label(**_clean_kwargs(translation_fidelity_score=0.5)) == "low"

    def test_translation_fidelity_below_half_is_low(self):
        assert confidence_label(**_clean_kwargs(translation_fidelity_score=0.25)) == "low"

    def test_dropped_entity_is_low(self):
        assert confidence_label(**_clean_kwargs(dropped_entities=1)) == "low"

    def test_dropped_metaphor_is_low(self):
        assert confidence_label(**_clean_kwargs(dropped_metaphors=1)) == "low"

    def test_review_item_is_low(self):
        assert confidence_label(**_clean_kwargs(review_items_count=1)) == "low"

    def test_failed_status_is_low(self):
        assert confidence_label(**_clean_kwargs(status="failed")) == "low"

    def test_salvaged_status_is_low(self):
        assert confidence_label(**_clean_kwargs(status="salvaged")) == "low"

    def test_alignment_below_60_is_low(self):
        assert confidence_label(**_clean_kwargs(alignment_conf=0.59)) == "low"

    def test_low_stanza_ratio_over_half_is_low(self):
        assert confidence_label(**_clean_kwargs(low_stanza_ratio=0.51)) == "low"

    def test_marginal_alignment_is_medium(self):
        assert confidence_label(**_clean_kwargs(alignment_conf=0.70)) == "medium"

    def test_alignment_75_boundary_is_high(self):
        assert confidence_label(**_clean_kwargs(alignment_conf=0.75)) == "high"


# ── Confidence: integration through assemble_annotation ───────────────────────
class TestAssembleConfidence:
    def test_clean_poem_is_high(self):
        poem = _poem(1)
        gated = _gated_payload(poem, tq="faithful")
        checks = {"entities_total": 0, "entities_dropped": 0, "metaphors_total": 0, "metaphors_dropped": 0}
        annotation, review_items, needs_review, confidence = assemble_annotation(
            poem, gated, source_term_checks=checks, gate_review_items=[],
            status="completed", model="gemini-chunked", poem_record=None,
        )
        assert confidence == "high"
        assert needs_review is False
        assert review_items == []

    def test_dropped_metaphor_blocks_high_and_flags_review(self):
        poem = _poem(1)
        gated = _gated_payload(poem, tq="faithful")
        checks = {"entities_total": 0, "entities_dropped": 0, "metaphors_total": 2, "metaphors_dropped": 1}
        gate_items = [{"field_path": "annotation.stanzas[1].metaphor_spans", "severity": "low",
                       "resolved_value": "dropped", "model_value": "x", "note": "metaphor_source_term_not_in_source"}]
        annotation, review_items, needs_review, confidence = assemble_annotation(
            poem, gated, source_term_checks=checks, gate_review_items=gate_items,
            status="completed", model="gemini-chunked", poem_record=None,
        )
        assert confidence == "low"
        assert needs_review is True
        assert annotation["annotation_stats"]["confidence"] == "low"

    def test_low_fidelity_blocks_high(self):
        poem = _poem(1)
        gated = _gated_payload(poem, tq="lost", loss_note="all imagery lost")  # fidelity 0.0
        checks = {"entities_total": 0, "entities_dropped": 0, "metaphors_total": 0, "metaphors_dropped": 0}
        annotation, review_items, needs_review, confidence = assemble_annotation(
            poem, gated, source_term_checks=checks, gate_review_items=[],
            status="completed", model="gemini-chunked", poem_record=None,
        )
        assert confidence == "low"


# ── Human-review routing invariant (assemble) ─────────────────────────────────
class TestNeedsReviewInvariant:
    def test_nonempty_review_items_forces_needs_review(self):
        poem = _poem(1)
        gated = _gated_payload(poem, tq="faithful")
        checks = {"entities_total": 0, "entities_dropped": 0, "metaphors_total": 0, "metaphors_dropped": 0}
        # A review item with no other failing signal must still flag the poem.
        gate_items = [_review_item(1)]
        _, review_items, needs_review, _ = assemble_annotation(
            poem, gated, source_term_checks=checks, gate_review_items=gate_items,
            status="completed", model="gemini-chunked", poem_record=None,
        )
        assert len(review_items) >= 1
        assert needs_review is True


# ── Human-review queue export (output) ────────────────────────────────────────
class TestReviewQueueExport:
    def test_every_review_item_exported(self):
        outputs = [{
            "poem_id": "P1", "poem_title": "T1", "language": "Bengali", "status": "completed",
            "needs_human_review": True,
            "review_items": [_review_item(1), _review_item(2)],
        }]
        rows = build_review_rows(outputs)
        assert len(rows) == 2
        assert {r["field_path"] for r in rows} == {"annotation.stanzas[1]", "annotation.stanzas[2]"}

    def test_review_items_exported_even_if_flag_false(self):
        # Defensive: even a mislabeled / legacy file must not hide its review items.
        outputs = [{
            "poem_id": "P2", "poem_title": "T2", "language": "Hindi", "status": "completed",
            "needs_human_review": False,
            "review_items": [_review_item(1)],
        }]
        rows = build_review_rows(outputs)
        assert len(rows) == 1
        assert rows[0]["poem_id"] == "P2"

    def test_empty_review_items_no_rows(self):
        outputs = [{
            "poem_id": "P3", "poem_title": "T3", "language": "Telugu", "status": "completed",
            "needs_human_review": False, "review_items": [],
        }]
        assert build_review_rows(outputs) == []

    def test_queue_row_count_matches_item_count_per_poem(self):
        outputs = [
            {"poem_id": "P1", "poem_title": "T1", "language": "Bengali", "status": "completed",
             "needs_human_review": True, "review_items": [_review_item(i) for i in range(5)]},
            {"poem_id": "P2", "poem_title": "T2", "language": "Hindi", "status": "salvaged",
             "needs_human_review": True, "review_items": [_review_item(0)]},
        ]
        rows = build_review_rows(outputs)
        for out in outputs:
            poem_rows = [r for r in rows if r["poem_id"] == out["poem_id"]]
            assert len(poem_rows) == len(out["review_items"])
