from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config import SCHEMA_VERSION, PROMPT_VERSION, GEMINI_PRIMARY
from .dataset import PreprocessedPoem
from .schema import STATUS_PENDING


def normalize_review_state(output: dict[str, Any]) -> bool:
    """Re-derive needs_human_review and confidence from the FINAL stored state.

    This is the safety net required by the human-review invariant: it recomputes
    both fields from the annotation that is actually on disk, so an output can
    never end up with review_items present but needs_human_review=False (which
    would hide those items from the queue), nor with a confidence label that
    contradicts dropped content / review items / low fidelity.

    Recomputation uses only already-stored stats (no model calls), so it is safe
    to run over previously written outputs. Returns True if anything changed.
    """
    from .assemble import confidence_label  # local import avoids any import cycle

    if output.get("status") == STATUS_PENDING:
        return False

    ann = output.get("annotation", {})
    stats = ann.get("annotation_stats", {})
    checks = stats.get("source_term_checks", {})
    review_items = output.get("review_items", []) or []
    review_count = len(review_items)

    status = output.get("status", "")
    model = output.get("model", "")
    dropped_entities = int(checks.get("entities_dropped", 0) or 0)
    dropped_metaphors = int(checks.get("metaphors_dropped", 0) or 0)
    low_conf_stanzas = int(stats.get("low_confidence_stanza_count", 0) or 0)
    stanza_count = max(len(ann.get("stanzas", [])) or output.get("preprocessing", {}).get("stanza_count", 0), 1)
    low_stanza_ratio = low_conf_stanzas / stanza_count
    fidelity = float(ann.get("translation_fidelity_score", 0.0) or 0.0)
    alignment_conf = float(
        stats.get("alignment_confidence",
                  output.get("preprocessing", {}).get("alignment_confidence", 0.0)) or 0.0
    )
    alignment_risk = output.get("preprocessing", {}).get("alignment_status") == "alignment_risk"

    new_needs_review = (
        status in ("failed", "salvaged")
        or alignment_risk
        or dropped_entities > 0
        or dropped_metaphors > 0
        or review_count > 0
        or low_stanza_ratio > 0.5
        or model == "gemini-3-flash"
    )
    new_confidence = confidence_label(
        alignment_conf=alignment_conf,
        status=status,
        dropped_entities=dropped_entities,
        dropped_metaphors=dropped_metaphors,
        review_items_count=review_count,
        translation_fidelity_score=fidelity,
        low_stanza_ratio=low_stanza_ratio,
    )

    changed = False
    if output.get("needs_human_review") != new_needs_review:
        output["needs_human_review"] = new_needs_review
        changed = True
    if stats.get("confidence") != new_confidence:
        stats["confidence"] = new_confidence
        changed = True
    if stats.get("review_item_count") != review_count:
        stats["review_item_count"] = review_count
        changed = True
    return changed


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def output_path_for_poem(poem_id: str, output_dir: Path, language: str = "") -> Path:
    if language:
        lang_dir = output_dir / language
        lang_dir.mkdir(parents=True, exist_ok=True)
        return lang_dir / f"{poem_id}.json"
    return output_dir / f"{poem_id}.json"


def build_pending_output(poem: PreprocessedPoem) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "poem_id": poem.poem_id,
        "poem_title": poem.poem_title,
        "language": poem.language,
        "original_poem": poem.original_poem,
        "translated_poem": poem.translated_poem,
        "status": STATUS_PENDING,
        "model": GEMINI_PRIMARY,
        "needs_human_review": False,
        "preprocessing": {
            "stanza_count": len(poem.stanzas),
            "source_stanza_count": poem.source_stanza_count,
            "translated_stanza_count": poem.translated_stanza_count,
            "alignment_status": poem.alignment_status,
            "alignment_confidence": poem.alignment_confidence,
            "alignment_note": poem.alignment_note,
            "stanzas": [{"stanza_index": s.stanza_index, "line_count": s.line_count,
                         "source_lines": s.source_lines, "translated_lines": s.translated_lines}
                        for s in poem.stanzas],
        },
        "annotation": {
            "recitation_style": "",
            "emotional_arc": "",
            "translation_fidelity_score": 0.0,
            "stanzas": [{"stanza_index": s.stanza_index, "line_count": s.line_count,
                         "source_lines": s.source_lines, "translated_lines": s.translated_lines,
                         "emotion": "", "tone": "", "translation_quality": "",
                         "loss_note": "", "metaphor_spans": []}
                        for s in poem.stanzas],
            "cultural_entities": [],
            "annotation_stats": {
                "model": GEMINI_PRIMARY,
                "alignment_status": poem.alignment_status,
                "alignment_confidence": poem.alignment_confidence,
                "source_term_checks": {"entities_total": 0, "entities_dropped": 0,
                                       "metaphors_total": 0, "metaphors_dropped": 0},
                "low_confidence_stanza_count": 0,
                "review_item_count": 0,
                "confidence": "pending",
            },
        },
        "review_items": [],
        "_raw": {},
    }


def build_summary_rows(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for out in outputs:
        ann = out.get("annotation", {})
        stats = ann.get("annotation_stats", {})
        checks = stats.get("source_term_checks", {})
        rows.append({
            "schema_version": out.get("schema_version", ""),
            "prompt_version": out.get("prompt_version", ""),
            "poem_id": out.get("poem_id", ""),
            "poem_title": out.get("poem_title", ""),
            "language": out.get("language", ""),
            "status": out.get("status", ""),
            "model": out.get("model", ""),
            "confidence": stats.get("confidence", ""),
            "needs_human_review": out.get("needs_human_review", False),
            "stanza_count": out.get("preprocessing", {}).get("stanza_count", 0),
            "alignment_status": out.get("preprocessing", {}).get("alignment_status", ""),
            "alignment_confidence": out.get("preprocessing", {}).get("alignment_confidence", 0.0),
            "entities_dropped": checks.get("entities_dropped", 0),
            "metaphors_dropped": checks.get("metaphors_dropped", 0),
            "low_confidence_stanza_count": stats.get("low_confidence_stanza_count", 0),
            "translation_fidelity_score": ann.get("translation_fidelity_score", 0.0),
            "review_item_count": stats.get("review_item_count", 0),
        })
    return rows


def build_review_rows(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Export EVERY review item, regardless of the needs_human_review flag.

    Invariant: the number of queue rows for a poem equals len(review_items) in
    that poem's annotation. We deliberately do NOT gate on needs_human_review —
    gating there is what previously hid review items from the queue. assemble.py
    already guarantees needs_human_review=True whenever review_items is non-empty;
    exporting unconditionally here makes silent loss impossible even for older or
    externally-edited annotation files.
    """
    rows = []
    for out in outputs:
        for item in out.get("review_items", []):
            rows.append({
                "poem_id": out.get("poem_id", ""),
                "poem_title": out.get("poem_title", ""),
                "language": out.get("language", ""),
                "status": out.get("status", ""),
                "field_path": item.get("field_path", ""),
                "severity": item.get("severity", ""),
                "resolved_value": item.get("resolved_value", ""),
                "model_value": item.get("model_value", ""),
                "note": item.get("note", ""),
            })
    return rows


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        if not fieldnames:
            f.write("")
            return
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
