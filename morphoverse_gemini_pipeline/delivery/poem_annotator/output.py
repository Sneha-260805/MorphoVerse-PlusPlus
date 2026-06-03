from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config import SCHEMA_VERSION, PROMPT_VERSION, GEMINI_PRIMARY
from .dataset import PreprocessedPoem
from .schema import STATUS_PENDING


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
    rows = []
    for out in outputs:
        if not out.get("needs_human_review"):
            continue
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
