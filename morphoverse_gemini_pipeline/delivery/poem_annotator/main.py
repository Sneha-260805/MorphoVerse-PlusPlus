from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from api import DEFAULT_BASE_URL
from .config import (
    DATASET_PATH,
    API_TOKEN,
    TOKEN_PLACEHOLDER,
    SUMMARY_FILENAME,
    HUMAN_REVIEW_FILENAME,
    GEMINI_PRIMARY,
    USE_CHUNKED_GEMINI,
    SCHEMA_VERSION,
    PROMPT_VERSION,
    SUPPORTED_LANGUAGES,
    DEFAULT_POEMS_PER_LANGUAGE,
    REQUIRED_DATASET_KEYS,
)
from .dataset import load_dataset_file, resolve_dataset_path, preprocess_poem, PreprocessedPoem
from .models import fetch_gemini_annotation, apply_source_term_gate
from .assemble import assemble_annotation
from .schema import STATUS_COMPLETED, STATUS_SALVAGED, STATUS_FAILED
from .shared_prompt_builder import build_prompt_bundle as build_shared_bundle
from .output import (
    output_path_for_poem,
    build_pending_output,
    load_json_file,
    write_json_file,
    build_summary_rows,
    build_review_rows,
    write_csv_rows,
    normalize_review_state,
)

# ── Excluded poems (skipped) ──────────────────────────────────────────────────
EXCLUDED_POEM_IDS = {"MV++_0056", "MV++_0059", "MV++_1429", "MV++_1431"}

# Language -> data-only module under poem_annotator.languages
_LANGUAGE_MODULES = {
    "Assamese": "assamese", "Bengali": "bengali", "Bodo": "bodo", "Dogri": "dogri",
    "Gujarati": "gujarati", "Hindi": "hindi", "Kannada": "kannada", "Kashmiri": "kashmiri",
    "Konkani": "konkani", "Malayalam": "malayalam", "Manipuri": "manipuri", "Marathi": "marathi",
    "Odia": "odia", "Punjabi": "punjabi", "Rajasthani": "rajasthani", "Sanskrit": "sanskrit",
    "Santhali": "santhali", "Sindhi": "sindhi", "Tamil": "tamil", "Telugu": "telugu", "Urdu": "urdu",
}

ALTERNATIVE_KEY_MAP = {
    "poem_id": "poem_id", "poem id": "poem_id", "Poem_ID": "poem_id", "Poem ID": "poem_id",
    "poemID": "poem_id", "id": "poem_id",
    "language": "language", "Language": "language", "lang": "language",
    "poem_title": "poem_title", "poem title": "poem_title", "Poem_Title": "poem_title",
    "Poem Title": "poem_title", "title": "poem_title",
    "original_poem": "original_poem", "original poem": "original_poem",
    "Original_Poem": "original_poem", "Original Poem": "original_poem",
    "translated_poem": "translated_poem", "translated poem": "translated_poem",
    "Translated_Poem": "translated_poem", "Translated Poem": "translated_poem",
}


def normalize_record_keys(record: dict) -> dict:
    return {ALTERNATIVE_KEY_MAP.get(k, k): v for k, v in record.items()}


def _load_language_data(language: str):
    package = __package__ or "poem_annotator"
    module_stem = _LANGUAGE_MODULES.get(language, "generic")
    try:
        mod = importlib.import_module(f"{package}.languages.{module_stem}")
    except ModuleNotFoundError:
        mod = importlib.import_module(f"{package}.languages.generic")
    return getattr(mod, "EXAMPLES", []), getattr(mod, "LANGUAGE_NOTE", "")


_PROMPT_CHAR_LIMIT = 8_500    # sys + user chars above which we strip EXAMPLES section


def _strip_examples(user_prompt: str) -> str:
    """Remove the EXAMPLES section from a user prompt to shorten long-poem requests."""
    marker = "\nEXAMPLES:\n"
    idx = user_prompt.find(marker)
    if idx == -1:
        return user_prompt
    return user_prompt[:idx].rstrip()


def build_prompt_bundle(poem: PreprocessedPoem, semantic_context: dict) -> tuple[str, str, str]:
    package = __package__ or "poem_annotator"
    module_stem = _LANGUAGE_MODULES.get(poem.language, "generic")
    try:
        mod = importlib.import_module(f"{package}.languages.{module_stem}")
        if hasattr(mod, "build_prompt_bundle_for_model"):
            sys_p, usr_p, rep_p = mod.build_prompt_bundle_for_model(poem, GEMINI_PRIMARY, semantic_context)
        else:
            raise AttributeError("no build_prompt_bundle_for_model")
    except Exception:
        examples, note = _load_language_data(poem.language)
        sys_p, usr_p, rep_p = build_shared_bundle(poem, examples, note, semantic_context=semantic_context)

    # For long poems whose total prompt would exceed the proxy's token ceiling,
    # drop the EXAMPLES section to free up output budget.
    if len(sys_p) + len(usr_p) > _PROMPT_CHAR_LIMIT:
        usr_p = _strip_examples(usr_p)

    return sys_p, usr_p, rep_p


def get_context(record: dict[str, str]) -> dict[str, Any]:
    """Try to get IndicBERT semantic hints; fall back to {} on any error.
    Returns {} when torch/sentence-transformers are unavailable (e.g. broken DLL).
    """
    try:
        from .indic_bert_context import get_context_safe
        return get_context_safe(record)
    except Exception:
        return {}


# ── Token / selection helpers ─────────────────────────────────────────────────
def resolve_api_token() -> str:
    env_token = os.getenv("LLM_PROXY_TOKEN", "").strip()
    if env_token:
        return env_token
    config_token = API_TOKEN.strip()
    if config_token and config_token != TOKEN_PLACEHOLDER:
        return config_token
    raise ValueError("Set LLM_PROXY_TOKEN before running (Gemini-only pipeline).")


def parse_poem_count(value: str | int) -> int | str:
    if value == "all" or (isinstance(value, str) and value.strip().lower() == "all"):
        return "all"
    count = int(value)
    if count < 0:
        raise ValueError("Poem count cannot be negative.")
    return count


def parse_language_overrides(values: list[str]) -> dict[str, int | str]:
    overrides: dict[str, int | str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Expected LANGUAGE=COUNT, got '{item}'.")
        lang, raw = item.split("=", 1)
        lang = lang.strip()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language override: {lang}")
        overrides[lang] = parse_poem_count(raw)
    return overrides


def merge_poem_limits(overrides: dict[str, int | str] | None = None) -> dict[str, int | str]:
    merged = {lang: DEFAULT_POEMS_PER_LANGUAGE.get(lang, "all") for lang in SUPPORTED_LANGUAGES}
    if overrides:
        merged.update(overrides)
    return merged


def select_poems(dataset, poems_per_language, *, poem_ids=None, limit=None):
    selected: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    id_filter = {pid.strip() for pid in (poem_ids or []) if pid.strip()}
    for record in dataset:
        if id_filter and record["poem_id"] not in id_filter:
            continue
        if record["poem_id"] in EXCLUDED_POEM_IDS:
            continue
        lang_limit = poems_per_language.get(record["language"], "all")
        if lang_limit != "all" and counts[record["language"]] >= lang_limit:
            continue
        selected.append(record)
        counts[record["language"]] += 1
        if limit is not None and len(selected) >= limit:
            break
    return selected


def is_output_current(output: dict[str, Any]) -> bool:
    if output.get("schema_version") != SCHEMA_VERSION or output.get("prompt_version") != PROMPT_VERSION:
        return False
    ann = output.get("annotation", {})
    if "translation_fidelity_score" not in ann:
        return False
    if "alignment_confidence" not in output.get("preprocessing", {}):
        return False
    # Reject any stale field that must not exist anymore.
    for stanza in ann.get("stanzas", []):
        if "visual_motifs" in stanza or "scene" in stanza:
            return False
    return True


def should_skip_output(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        existing = load_json_file(path)
    except (json.JSONDecodeError, OSError):
        return False
    if not is_output_current(existing):
        return False
    # Only skip poems that already have a valid terminal annotation.
    # "failed" and "pending" must be retried, not silently skipped.
    return existing.get("status") in (STATUS_COMPLETED, STATUS_SALVAGED)


# ── Core processing (Gemini only) ─────────────────────────────────────────────
async def process_poem(record, *, token, base_url, output_dir, request_fn=None) -> dict[str, Any]:
    poem = preprocess_poem(record)
    semantic_context = get_context(record)
    out_path = output_path_for_poem(poem.poem_id, output_dir, language=poem.language)
    if should_skip_output(out_path):
        return load_json_file(out_path)

    pending = build_pending_output(poem)
    write_json_file(out_path, pending)

    # Gemini-only chunked path (default). The one-shot path is kept for tests that
    # inject a request_fn, and is selectable via USE_CHUNKED_GEMINI=0.
    if USE_CHUNKED_GEMINI and request_fn is None:
        from .gemini_chunked import annotate_poem_chunked
        result = await asyncio.to_thread(annotate_poem_chunked, poem, token, base_url)
    else:
        system_prompt, user_prompt, repair_prompt = build_prompt_bundle(poem, semantic_context)
        result = await fetch_gemini_annotation(poem, system_prompt, user_prompt, repair_prompt,
                                               token, base_url, request_fn=request_fn)

    if result["status"] != "valid":
        failed = pending | {
            "status": STATUS_FAILED,
            "needs_human_review": True,
            "model": result.get("model", GEMINI_PRIMARY),
            "_raw": {"status": result["status"], "discard_reason": result["discard_reason"],
                     "raw_text": result.get("raw_text", "")},
        }
        failed["annotation"]["annotation_stats"]["confidence"] = "low"
        write_json_file(out_path, failed)
        return failed

    gate = apply_source_term_gate(result["parsed"], poem)
    status = STATUS_SALVAGED if gate["source_term_checks"]["entities_dropped"] > 0 else STATUS_COMPLETED

    annotation, review_items, needs_review, confidence = assemble_annotation(
        poem, gate["payload"],
        source_term_checks=gate["source_term_checks"],
        gate_review_items=gate["review_items"],
        status=status,
        model=result["model"],
        poem_record=record,
    )

    completed = pending | {
        "status": status,
        "model": result["model"],
        "needs_human_review": needs_review,
        "annotation": annotation,
        "review_items": review_items,
        "_raw": {"prompt_kind": result["prompt_kind"], "retry_count": result["retry_count"]},
    }
    write_json_file(out_path, completed)
    return completed


async def run_pipeline(config: "RuntimeConfig", request_fn=None) -> list[dict[str, Any]]:
    input_folder = Path(config.input_folder or "filtered_poems")
    output_dir = Path(config.output_dir or "output")
    output_dir.mkdir(parents=True, exist_ok=True)
    token = resolve_api_token()

    all_results: list[dict[str, Any]] = []
    all_datasets: list[dict[str, str]] = []

    for json_file in sorted(input_folder.glob("*.json")):
        dataset = load_dataset_file(json_file)
        dataset = [p for p in dataset if p["poem_id"] not in EXCLUDED_POEM_IDS]
        dataset = [p for p in dataset if p["language"] in SUPPORTED_LANGUAGES]
        selected = select_poems(dataset, config.poems_per_language, poem_ids=config.poem_ids, limit=config.limit)

        for record in selected:
            print(f"Processing poem {record['poem_id']} from {json_file.name} …")
            result = await process_poem(record, token=token, base_url=config.base_url,
                                        output_dir=output_dir, request_fn=request_fn)
            all_results.append(result)
            print(f"  -> {result.get('status', 'unknown')} (confidence="
                  f"{result.get('annotation', {}).get('annotation_stats', {}).get('confidence', '?')})")
        all_datasets.extend(dataset)

    existing = collect_existing_outputs(all_datasets, output_dir)
    if config.write_summary:
        write_csv_rows(output_dir / SUMMARY_FILENAME, build_summary_rows(existing))
    if config.write_human_review_queue:
        write_csv_rows(output_dir / HUMAN_REVIEW_FILENAME, build_review_rows(existing))
    return all_results


def collect_existing_outputs(dataset, output_dir: Path) -> list[dict[str, Any]]:
    """Load every existing output, re-deriving needs_human_review + confidence from
    its final stored state (and persisting any correction) so the summary/queue
    CSVs and the on-disk JSON can never disagree with the review-item invariant."""
    outputs = []
    for rec in dataset:
        path = output_path_for_poem(rec["poem_id"], output_dir, language=rec["language"])
        if not path.exists():
            continue
        try:
            out = load_json_file(path)
        except (json.JSONDecodeError, OSError):
            continue
        if normalize_review_state(out):
            write_json_file(path, out)
        outputs.append(out)
    return outputs


class RuntimeConfig:
    def __init__(self, dataset_path, poems_per_language, poem_ids, limit, output_dir,
                 write_summary, write_human_review_queue, base_url, input_folder=None):
        self.dataset_path = dataset_path
        self.poems_per_language = poems_per_language
        self.poem_ids = poem_ids or []
        self.limit = limit
        self.output_dir = output_dir
        self.write_summary = write_summary
        self.write_human_review_queue = write_human_review_queue
        self.base_url = base_url
        self.input_folder = input_folder


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Gemini-only poem annotation pipeline.")
    parser.add_argument("--dataset", help="Path to dataset.json (only if --input-folder not used).")
    parser.add_argument("--input-folder", default="filtered_poems", help="Folder of poem JSON files.")
    parser.add_argument("--poems-per-language", nargs="*", default=[], help="Overrides like Hindi=3 Telugu=all")
    parser.add_argument("--poem-id", action="append", default=[], help="Repeatable poem_id filter.")
    parser.add_argument("--limit", type=int, help="Optional cap after language filtering.")
    parser.add_argument("--output-dir", default="output", help="Output directory.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Proxy base URL override.")
    parser.add_argument("--no-summary", action="store_true")
    parser.add_argument("--no-human-review-queue", action="store_true")
    return parser.parse_args(argv)


def build_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    if args.input_folder:
        dataset_path = ""
    elif args.dataset:
        dataset_path = resolve_dataset_path(args.dataset)
    else:
        dataset_path = resolve_dataset_path(DATASET_PATH)
    overrides = parse_language_overrides(args.poems_per_language)
    poems_per_language = merge_poem_limits(overrides)
    return RuntimeConfig(
        dataset_path=dataset_path,
        poems_per_language=poems_per_language,
        poem_ids=args.poem_id,
        limit=args.limit,
        output_dir=Path(args.output_dir),
        write_summary=not args.no_summary,
        write_human_review_queue=not args.no_human_review_queue,
        base_url=args.base_url,
        input_folder=args.input_folder,
    )


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        config = build_runtime_config(args)
        results = asyncio.run(run_pipeline(config))
    except Exception as exc:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    completed = sum(1 for r in results if r.get("status") == STATUS_COMPLETED)
    salvaged = sum(1 for r in results if r.get("status") == STATUS_SALVAGED)
    failed = sum(1 for r in results if r.get("status") == STATUS_FAILED)
    print(f"Processed {len(results)} poem(s): completed={completed}, salvaged={salvaged}, failed={failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
