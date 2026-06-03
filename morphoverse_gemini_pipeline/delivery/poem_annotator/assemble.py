"""Single-model annotation assembly. Replaces voting.py.

There is no ensemble, so there is no majority vote, no tie-break, and no
per-field source-model selection. Confidence is derived from evidence quality
(alignment, source-term pass rate, translation mix) — never auto-"high".
"""
from __future__ import annotations

from typing import Any

from .dataset import PreprocessedPoem
from .schema import ALIGNMENT_RISK

TRANSLATION_SCORE = {"faithful": 1.0, "partial": 0.5, "lost": 0.0}


def confidence_label(alignment_conf: float, status: str, dropped_entities: int, low_stanza_ratio: float) -> str:
    if status in ("failed", "salvaged") or dropped_entities or alignment_conf < 0.60 or low_stanza_ratio > 0.5:
        return "low"
    if alignment_conf < 0.75:
        return "medium"
    return "high"


def assemble_annotation(
    poem: PreprocessedPoem,
    gated_payload: dict[str, Any],
    *,
    source_term_checks: dict[str, int],
    gate_review_items: list[dict[str, Any]],
    status: str,
    model: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], bool, str]:
    review_items: list[dict[str, Any]] = list(gate_review_items)
    alignment_risk = poem.alignment_status == ALIGNMENT_RISK

    resolved_stanzas: list[dict[str, Any]] = []
    fidelity_sum = 0.0
    low_conf_stanzas = 0

    for stanza in poem.stanzas:
        sv = gated_payload["stanzas"][stanza.stanza_index - 1]
        tq = sv["translation_quality"]
        loss_note = "" if tq == "faithful" else sv["loss_note"]
        fidelity_sum += TRANSLATION_SCORE.get(tq, 0.0)

        # A stanza is low-confidence if alignment is risky, or it is "lost" with no explanation.
        stanza_low = alignment_risk or (tq == "lost" and not loss_note)
        if stanza_low:
            low_conf_stanzas += 1
            if alignment_risk:
                review_items.append({
                    "field_path": f"annotation.stanzas[{stanza.stanza_index}]",
                    "severity": "medium",
                    "resolved_value": tq,
                    "model_value": tq,
                    "note": "stanza_in_alignment_risk_poem",
                })

        resolved_stanzas.append({
            "stanza_index": stanza.stanza_index,
            "line_count": stanza.line_count,
            "source_lines": stanza.source_lines,
            "translated_lines": stanza.translated_lines,
            "emotion": sv["emotion"],
            "tone": sv["tone"],
            "translation_quality": tq,
            "loss_note": loss_note,
            "metaphor_spans": sv["metaphor_spans"],
        })

    resolved_entities = [{
        "term": e["term"],
        "romanization": e["romanization"],
        "category": e["category"],
        "stanza_index": e["stanza_index"],
        "preserved": e["preserved"],
        "translation_note": e["translation_note"],
    } for e in gated_payload["cultural_entities"]]

    stanza_count = max(len(poem.stanzas), 1)
    low_stanza_ratio = low_conf_stanzas / stanza_count
    dropped_entities = source_term_checks.get("entities_dropped", 0)

    needs_human_review = (
        status in ("failed", "salvaged")
        or alignment_risk
        or dropped_entities > 0
        or low_stanza_ratio > 0.5
        or model == "gemini-3-flash"
    )

    confidence = confidence_label(poem.alignment_confidence, status, dropped_entities, low_stanza_ratio)

    annotation = {
        "recitation_style": gated_payload["recitation_style"],
        "emotional_arc": gated_payload["emotional_arc"],
        "translation_fidelity_score": round(fidelity_sum / stanza_count, 6),
        "stanzas": resolved_stanzas,
        "cultural_entities": resolved_entities,
        "annotation_stats": {
            "model": model,
            "alignment_status": poem.alignment_status,
            "alignment_confidence": poem.alignment_confidence,
            "source_term_checks": source_term_checks,
            "low_confidence_stanza_count": low_conf_stanzas,
            "review_item_count": len(review_items),
            "confidence": confidence,
        },
    }
    return annotation, review_items, needs_human_review, confidence
