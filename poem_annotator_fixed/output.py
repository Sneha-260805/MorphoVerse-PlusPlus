from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config import SCHEMA_VERSION, PROMPT_VERSION, VOTING_MODELS
from .dataset import PreprocessedPoem  # needed for type hint


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


def build_pending_output(poem: PreprocessedPoem, selected_models: list[str]) -> dict[str, Any]:
    vote_slots = list(dict.fromkeys(selected_models + (["gemini-3-flash"] if "gemini" in selected_models else [])))
    return {
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "poem_id": poem.poem_id,
        "poem_title": poem.poem_title,
        "language": poem.language,
        "original_poem": poem.original_poem,
        "translated_poem": poem.translated_poem,
        "status": "pending",
        "agreement": "pending",
        "vote_basis": "pending",
        "needs_human_review": False,
        "preprocessing": {
            "stanza_count": len(poem.stanzas),
            "source_stanza_count": poem.source_stanza_count,
            "translated_stanza_count": poem.translated_stanza_count,
            "alignment_status": poem.alignment_status,
            "alignment_note": poem.alignment_note,
            "stanzas": [{"stanza_index": s.stanza_index, "line_count": s.line_count,
                         "source_lines": s.source_lines, "translated_lines": s.translated_lines}
                        for s in poem.stanzas],
        },
        "annotation": {
            "recitation_style": {"value": "", "agreement": "pending", "source_model": None},
            "emotional_arc": {"value": "", "agreement": "pending", "source_model": None},
            "translation_fidelity_score": 0.0,
            "stanzas": [{"stanza_index": s.stanza_index, "line_count": s.line_count,
                         "source_lines": s.source_lines, "translated_lines": s.translated_lines,
                         "emotion": {"value": "", "agreement": "pending", "source_model": None},
                         "tone": {"value": "", "agreement": "pending", "source_model": None},
                         "translation_quality": {"value": "", "agreement": "pending", "source_model": None},
                         "loss_note": {"value": "", "agreement": "pending", "source_model": None},
                         "metaphor_spans": [],
                         "visual_motifs": []}
                        for s in poem.stanzas],
            "cultural_entities": [],
            "agreement_stats": {
                "selected_models": selected_models,
                "voting_models": [m for m in selected_models if m in VOTING_MODELS],
                "valid_models_total": 0,
                "valid_voting_models": 0,
                "low_stanza_count": 0,
                "medium_stanza_count": 0,
                "low_entity_count": 0,
                "review_item_count": 0,
                "vote_basis": "pending",
            },
        },
        "review_items": [],
        "_votes": {
            model: {"status": "pending", "retry_count": 0, "raw_text": "",
                    "parsed": None, "discard_reason": "", "comparison": None,
                    "is_voting_model": model in VOTING_MODELS, "prompt_kind": ""}
            for model in vote_slots
        },
    }


def build_summary_rows(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for out in outputs:
        ann = out.get("annotation", {})
        stats = ann.get("agreement_stats", {})
        rows.append({
            "schema_version": out.get("schema_version", ""),
            "prompt_version": out.get("prompt_version", ""),
            "poem_id": out.get("poem_id", ""),
            "poem_title": out.get("poem_title", ""),
            "language": out.get("language", ""),
            "status": out.get("status", ""),
            "agreement": out.get("agreement", ""),
            "vote_basis": out.get("vote_basis", ""),
            "needs_human_review": out.get("needs_human_review", False),
            "valid_models_total": stats.get("valid_models_total", 0),
            "valid_voting_models": stats.get("valid_voting_models", 0),
            "stanza_count": out.get("preprocessing", {}).get("stanza_count", 0),
            "low_stanza_count": stats.get("low_stanza_count", 0),
            "medium_stanza_count": stats.get("medium_stanza_count", 0),
            "low_entity_count": stats.get("low_entity_count", 0),
            "translation_fidelity_score": ann.get("translation_fidelity_score", 0.0),
            "alignment_status": out.get("preprocessing", {}).get("alignment_status", ""),
            "alignment_note": out.get("preprocessing", {}).get("alignment_note", ""),
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
                "vote_basis": out.get("vote_basis", ""),
                "field_path": item.get("field_path", ""),
                "agreement": item.get("agreement", ""),
                "resolved_value": item.get("resolved_value", ""),
                "claude_value": item.get("claude_value", ""),
                "gpt_value": item.get("gpt_value", ""),
                "gemini_value": item.get("gemini_value", ""),
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