"""MorphoVerse++ Schema v1.1 batch migration (5 poems per batch).

Reads source poems from repo-root output_jsons/, prefers existing annotations from
output_v3/ (then output_v2/, output_test/), writes to output_v1_1/ and reports/.

Does NOT overwrite original annotation directories.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from poem_annotator.config import (
    MIGRATION_BATCH_SIZE,
    MIGRATION_OUTPUT_DIR,
    MIGRATION_PROMPT_VERSION,
    MIGRATION_REPORTS_DIR,
    MIGRATION_SCHEMA_VERSION,
    MIGRATION_SOURCE_DIRS,
    USE_VERTEX_AI,
)
from poem_annotator.dataset import load_dataset_file
from poem_annotator.output import write_json_file, load_json_file
from poem_annotator.schema import (
    ALLOWED_EXPRESSION_TYPES,
    ALLOWED_VISUAL_PRIORITIES,
    SCHEMA_VERSION_V1_1,
)
from poem_annotator.span_utils import find_exact_substring, find_translation_span
from poem_annotator.v1_1_validate import validate_v1_1_output


# ── Paths ─────────────────────────────────────────────────────────────────────
def repo_root(delivery_dir: Path) -> Path:
    return delivery_dir.parent.parent


def default_input_folder(delivery_dir: Path) -> Path:
    return repo_root(delivery_dir) / "output_jsons"


def delivery_dir() -> Path:
    return Path(__file__).resolve().parent.parent


# ── Classification ────────────────────────────────────────────────────────────
@dataclass
class MigrationAction:
    poem_id: str
    action: str  # preserve | transform | backfill | human_review | regenerate
    reasons: list[str] = field(default_factory=list)


def classify_existing(existing: dict[str, Any] | None) -> MigrationAction:
    poem_id = (existing or {}).get("poem_id", "?")
    if not existing:
        return MigrationAction(poem_id, "regenerate", ["no_existing_annotation"])

    status = existing.get("status", "")
    if status == "failed":
        return MigrationAction(poem_id, "regenerate", ["status_failed"])
    if status not in ("completed", "salvaged"):
        return MigrationAction(poem_id, "regenerate", [f"status_{status or 'missing'}"])

    ann = existing.get("annotation") or {}
    if not ann.get("stanzas"):
        return MigrationAction(poem_id, "regenerate", ["missing_stanzas"])

    reasons: list[str] = []
    action = "preserve"
    stats = ann.get("annotation_stats") or {}
    if existing.get("schema_version") != 5 and existing.get("schema_version") != "1.1":
        action = "transform"
        reasons.append("schema_version_upgrade")
    if status == "salvaged":
        action = "human_review"
        reasons.append("salvaged_status")
    if stats.get("confidence") == "low":
        action = "human_review"
        reasons.append("low_confidence")
    if existing.get("review_items"):
        action = "human_review"
        reasons.append("existing_review_items")
    checks = stats.get("source_term_checks") or {}
    if checks.get("entities_dropped") or checks.get("metaphors_dropped"):
        action = "human_review"
        reasons.append("dropped_terms")

    # All v1.1 outputs need new fields → always backfill at minimum
    if action == "preserve":
        action = "backfill"
        reasons.append("v1_1_field_backfill")
    elif action == "transform":
        reasons.append("v1_1_field_backfill")
    else:
        reasons.append("v1_1_field_backfill_with_review")

    return MigrationAction(poem_id, action, reasons)


def load_existing_annotation(
    poem_id: str,
    language: str,
    delivery: Path,
    source_dirs: tuple[str, ...],
) -> dict[str, Any] | None:
    for dirname in source_dirs:
        path = delivery / dirname / language / f"{poem_id}.json"
        if path.exists():
            try:
                return load_json_file(path)
            except (json.JSONDecodeError, OSError):
                continue
    return None


# ── Deterministic span / defaults ─────────────────────────────────────────────
def _default_visual_priority(category: str) -> str:
    if category in ("DEITY", "SACRED_RIVER", "MYTHOLOGICAL_EVENT", "FESTIVAL"):
        return "essential"
    if category in ("MUSICAL_TRADITION", "DEVOTIONAL_CONCEPT", "REGIONAL_SYMBOL"):
        return "supporting"
    return "optional"


def migrate_entity(entity: dict[str, Any], *, original: str, translated: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    review: list[dict[str, Any]] = []
    term = entity.get("term", "")
    src_span = find_exact_substring(term, original)
    if src_span is None:
        review.append({
            "field_path": "annotation.cultural_entities",
            "severity": "high",
            "resolved_value": None,
            "model_value": term,
            "note": "source_span_original_not_found",
        })

    tr_span = find_translation_span(
        term=term,
        romanization=entity.get("romanization", ""),
        translation_note=entity.get("translation_note", ""),
        translated_poem=translated,
        preserved=bool(entity.get("preserved")),
    )
    if tr_span is None and entity.get("preserved") is False:
        review.append({
            "field_path": "annotation.cultural_entities",
            "severity": "medium",
            "resolved_value": None,
            "model_value": term,
            "note": "source_span_translation_not_found",
        })

    out = {
        **entity,
        "source_span_original": src_span,
        "source_span_translation": tr_span,
        "visual_priority": entity.get("visual_priority") or _default_visual_priority(entity.get("category", "")),
        "acceptable_visual_variants": entity.get("acceptable_visual_variants") or [],
    }
    return out, review


def migrate_metaphor(span: dict[str, Any], *, original: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    review: list[dict[str, Any]] = []
    src = span.get("source_term", "")
    if find_exact_substring(src, original) is None:
        review.append({
            "field_path": "annotation.stanzas.metaphor_spans",
            "severity": "high",
            "resolved_value": None,
            "model_value": src,
            "note": "metaphor_source_not_in_original",
        })
    out = {
        **span,
        "expression_type": span.get("expression_type") or "metaphor",
        "literal_meaning": span.get("literal_meaning"),
        "metaphor_mapping": span.get("metaphor_mapping"),
    }
    return out, review


# ── Vertex backfill ─────────────────────────────────────────────────────────────
def vertex_backfill_entity(entity: dict[str, Any], *, original: str, translated: str) -> tuple[dict[str, Any], str | None]:
    if not USE_VERTEX_AI:
        return entity, None
    try:
        from vertex_client import generate_json
    except ImportError:
        return entity, "google-genai not installed"

    system = (
        "You backfill MorphoVerse++ v1.1 cultural cue fields. "
        "Return JSON only. Never invent source spans. "
        f"visual_priority must be one of: {list(ALLOWED_VISUAL_PRIORITIES)}."
    )
    user = json.dumps({
        "term": entity.get("term"),
        "category": entity.get("category"),
        "translation_note": entity.get("translation_note"),
        "original_excerpt": original[:800],
        "translation_excerpt": translated[:800],
        "required_output": {
            "visual_priority": "essential|supporting|optional|non_visual",
            "acceptable_visual_variants": ["culturally valid alternative visual descriptions"],
            "cultural_specificity_level": "high|medium|low or null",
            "visualization_difficulty": "easy|moderate|hard or null",
        },
    }, ensure_ascii=False)

    try:
        result = generate_json(system, user, max_output_tokens=1024)
    except Exception as exc:
        return entity, str(exc)

    if isinstance(result, dict):
        vp = result.get("visual_priority")
        if vp in ALLOWED_VISUAL_PRIORITIES:
            entity["visual_priority"] = vp
        variants = result.get("acceptable_visual_variants")
        if isinstance(variants, list) and variants:
            entity["acceptable_visual_variants"] = [str(v) for v in variants if str(v).strip()]
        for pilot in ("cultural_specificity_level", "visualization_difficulty"):
            if result.get(pilot) not in (None, ""):
                entity[pilot] = result[pilot]
    return entity, None


def vertex_backfill_metaphor(span: dict[str, Any], *, original: str, translated: str) -> tuple[dict[str, Any], str | None]:
    if not USE_VERTEX_AI:
        return span, None
    try:
        from vertex_client import generate_json
    except ImportError:
        return span, "google-genai not installed"

    system = (
        "You backfill MorphoVerse++ v1.1 figurative fields. Return JSON only. "
        f"expression_type must be one of: {list(ALLOWED_EXPRESSION_TYPES)}. "
        "literal_meaning and metaphor_mapping must be null unless genuinely applicable."
    )
    user = json.dumps({
        "source_term": span.get("source_term"),
        "abstract_meaning": span.get("abstract_meaning"),
        "original_excerpt": original[:800],
        "translation_excerpt": translated[:800],
    }, ensure_ascii=False)

    try:
        result = generate_json(system, user, max_output_tokens=768)
    except Exception as exc:
        return span, str(exc)

    if isinstance(result, dict):
        et = result.get("expression_type")
        if et in ALLOWED_EXPRESSION_TYPES:
            span["expression_type"] = et
        for key in ("literal_meaning", "metaphor_mapping"):
            val = result.get(key)
            span[key] = None if val in (None, "") else str(val)
    return span, None


# ── Core migration ──────────────────────────────────────────────────────────────
def migrate_poem(
    source_record: dict[str, str],
    existing: dict[str, Any] | None,
    action: MigrationAction,
    *,
    use_vertex: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (migrated_output, per_poem_report)."""
    original = source_record["original_poem"]
    translated = source_record["translated_poem"]
    report: dict[str, Any] = {
        "poem_id": source_record["poem_id"],
        "action": action.action,
        "reasons": action.reasons,
        "backfill": {"entities": 0, "metaphors": 0, "vertex_calls": 0, "vertex_errors": []},
        "regenerated": False,
    }

    if action.action == "regenerate" or not existing:
        report["regenerated"] = True
        report["regenerate_note"] = "full_regeneration_not_run_in_pilot;_no_v1_1_source"
        existing = existing or {
            "poem_id": source_record["poem_id"],
            "poem_title": source_record["poem_title"],
            "language": source_record["language"],
            "original_poem": original,
            "translated_poem": translated,
            "status": "failed",
            "annotation": {"stanzas": [], "cultural_entities": []},
            "review_items": [],
            "preprocessing": {},
        }

    migrated = copy.deepcopy(existing)
    migrated["schema_version"] = SCHEMA_VERSION_V1_1
    migrated["prompt_version"] = MIGRATION_PROMPT_VERSION
    migrated["migration"] = {
        "source_schema_version": existing.get("schema_version"),
        "source_prompt_version": existing.get("prompt_version"),
        "source_model": existing.get("model"),
        "migrated_at": datetime.now(timezone.utc).isoformat(),
        "action": action.action,
    }
    migrated["original_poem"] = original
    migrated["translated_poem"] = translated
    migrated["poem_title"] = source_record.get("poem_title", migrated.get("poem_title", ""))
    migrated["language"] = source_record["language"]

    ann = migrated.setdefault("annotation", {})
    new_review: list[dict[str, Any]] = list(migrated.get("review_items") or [])

    # Entities
    entities_out: list[dict[str, Any]] = []
    for ent in ann.get("cultural_entities") or []:
        ent_m, rev = migrate_entity(ent, original=original, translated=translated)
        ent_m, verr = vertex_backfill_entity(ent_m, original=original, translated=translated) if use_vertex else (ent_m, None)
        report["backfill"]["entities"] += 1
        if use_vertex:
            report["backfill"]["vertex_calls"] += 1
            if verr:
                report["backfill"]["vertex_errors"].append(f"entity:{ent.get('term')}: {verr}")
        new_review.extend(rev)
        entities_out.append(ent_m)
    ann["cultural_entities"] = entities_out

    # Metaphors
    stanzas_out: list[dict[str, Any]] = []
    for st in ann.get("stanzas") or []:
        st_copy = copy.deepcopy(st)
        spans_out: list[dict[str, Any]] = []
        for sp in st_copy.get("metaphor_spans") or []:
            sp_m, rev = migrate_metaphor(sp, original=original)
            sp_m, verr = vertex_backfill_metaphor(sp_m, original=original, translated=translated) if use_vertex else (sp_m, None)
            report["backfill"]["metaphors"] += 1
            if use_vertex:
                report["backfill"]["vertex_calls"] += 1
                if verr:
                    report["backfill"]["vertex_errors"].append(f"metaphor:{sp.get('source_term')}: {verr}")
            new_review.extend(rev)
            spans_out.append(sp_m)
        st_copy["metaphor_spans"] = spans_out
        stanzas_out.append(st_copy)
    ann["stanzas"] = stanzas_out

    migrated["review_items"] = new_review
    if new_review or action.action == "human_review":
        migrated["needs_human_review"] = True

    validation_errors = validate_v1_1_output(migrated)
    report["validation_errors"] = validation_errors
    report["validation_passed"] = len(validation_errors) == 0

    return migrated, report


# ── Batch orchestration ─────────────────────────────────────────────────────────
def collect_source_poems(input_folder: Path) -> list[dict[str, str]]:
    poems: list[dict[str, str]] = []
    for json_file in sorted(input_folder.glob("*_poems.json")):
        for record in load_dataset_file(json_file):
            poems.append(record)
    poems.sort(key=lambda r: r["poem_id"])
    return poems


def run_batch(
    *,
    delivery: Path,
    input_folder: Path,
    output_dir: Path,
    reports_dir: Path,
    source_dirs: tuple[str, ...],
    batch_index: int,
    batch_size: int,
    poem_ids: list[str] | None = None,
    use_vertex: bool = True,
) -> int:
    all_poems = collect_source_poems(input_folder)
    if poem_ids:
        id_set = set(poem_ids)
        all_poems = [p for p in all_poems if p["poem_id"] in id_set]
    else:
        start = batch_index * batch_size
        all_poems = all_poems[start : start + batch_size]

    if not all_poems:
        print("No poems selected for this batch.", file=sys.stderr)
        return 1

    batch_name = f"batch_{batch_index:03d}"
    batch_reports = reports_dir / batch_name
    batch_reports.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    migration_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    backfill_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    regeneration_rows: list[dict[str, Any]] = []

    for record in all_poems:
        poem_id = record["poem_id"]
        language = record["language"]
        existing = load_existing_annotation(poem_id, language, delivery, source_dirs)
        action = classify_existing(existing)
        migrated, poem_report = migrate_poem(
            record, existing, action, use_vertex=use_vertex,
        )

        out_path = output_dir / language / f"{poem_id}.json"
        write_json_file(out_path, migrated)

        migration_rows.append({
            "poem_id": poem_id,
            "language": language,
            "action": action.action,
            "reasons": ";".join(action.reasons),
            "source_found": existing is not None,
            "source_dir": next(
                (d for d in source_dirs if (delivery / d / language / f"{poem_id}.json").exists()),
                "",
            ),
            "output_path": str(out_path.relative_to(delivery)),
        })
        validation_rows.append({
            "poem_id": poem_id,
            "passed": poem_report["validation_passed"],
            "errors": "; ".join(poem_report.get("validation_errors") or []),
        })
        backfill_rows.append({
            "poem_id": poem_id,
            **poem_report.get("backfill", {}),
        })
        if poem_report.get("regenerated"):
            regeneration_rows.append({
                "poem_id": poem_id,
                "note": poem_report.get("regenerate_note", "regenerated"),
            })
        for item in migrated.get("review_items") or []:
            review_rows.append({"poem_id": poem_id, **item})

        print(f"  {poem_id}: action={action.action} valid={poem_report['validation_passed']}")

    # Write reports (JSON + CSV where useful)
    _write_json(batch_reports / "migration_report.json", {
        "batch": batch_name,
        "poem_count": len(all_poems),
        "rows": migration_rows,
    })
    _write_json(batch_reports / "validation_report.json", {
        "batch": batch_name,
        "passed": sum(1 for r in validation_rows if r["passed"]),
        "failed": sum(1 for r in validation_rows if not r["passed"]),
        "rows": validation_rows,
    })
    _write_json(batch_reports / "backfill_report.json", {
        "batch": batch_name,
        "rows": backfill_rows,
    })
    _write_json(batch_reports / "review_queue.json", {"batch": batch_name, "rows": review_rows})
    _write_json(batch_reports / "regeneration_report.json", {
        "batch": batch_name,
        "rows": regeneration_rows,
    })
    _write_csv(batch_reports / "review_queue.csv", review_rows)
    _write_csv(batch_reports / "migration_report.csv", migration_rows)

    print(f"Batch {batch_name}: migrated {len(all_poems)} poem(s)")
    print(f"  output  -> {output_dir}")
    print(f"  reports -> {batch_reports}")
    return 0


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    d = delivery_dir()
    p = argparse.ArgumentParser(description="Migrate MorphoVerse annotations to Schema v1.1 (batch of 5).")
    p.add_argument("--input-folder", type=Path, default=default_input_folder(d))
    p.add_argument("--output-dir", type=Path, default=d / MIGRATION_OUTPUT_DIR)
    p.add_argument("--reports-dir", type=Path, default=d / MIGRATION_REPORTS_DIR)
    p.add_argument("--source-dirs", nargs="*", default=list(MIGRATION_SOURCE_DIRS))
    p.add_argument("--batch-index", type=int, default=0, help="0-based batch index")
    p.add_argument("--batch-size", type=int, default=MIGRATION_BATCH_SIZE)
    p.add_argument("--poem-id", action="append", default=[], help="Optional explicit poem IDs")
    p.add_argument("--no-vertex", action="store_true", help="Skip Vertex AI backfill calls")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    delivery = delivery_dir()
    print(f"Migrating to schema {MIGRATION_SCHEMA_VERSION!r} (batch size {args.batch_size})")
    print(f"  input:  {args.input_folder}")
    print(f"  source: {args.source_dirs} (prefer first)")
    return run_batch(
        delivery=delivery,
        input_folder=args.input_folder,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        source_dirs=tuple(args.source_dirs),
        batch_index=args.batch_index,
        batch_size=args.batch_size,
        poem_ids=args.poem_id or None,
        use_vertex=not args.no_vertex and USE_VERTEX_AI,
    )


if __name__ == "__main__":
    raise SystemExit(main())
