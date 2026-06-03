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

from api import DEFAULT_BASE_URL, SUPPORTED_MODELS as PROXY_SUPPORTED_MODELS
from .config import (
    DATASET_PATH,
    API_TOKEN,
    TOKEN_PLACEHOLDER,
    SUMMARY_FILENAME,
    HUMAN_REVIEW_FILENAME,
    VOTING_MODELS,
    MODEL_ORDER,
    SCHEMA_VERSION,
    PROMPT_VERSION,
    SUPPORTED_LANGUAGES,
    DEFAULT_POEMS_PER_LANGUAGE,
    REQUIRED_DATASET_KEYS,
)
from .dataset import (
    load_dataset_file,
    resolve_dataset_path,
    preprocess_poem,
    PreprocessedPoem,
)

from .models import call_model_text, fetch_model_vote
from .output import (
    output_path_for_poem,
    build_pending_output,
    load_json_file,
    write_json_file,
    build_summary_rows,
    build_review_rows,
    write_csv_rows,
)
from .voting import resolve_annotation

# ── Excluded poems (will be skipped) ─────────────────────────────────────
EXCLUDED_POEM_IDS = {"MV++_0056", "MV++_0059", "MV++_1429", "MV++_1431"}

# ── Prompt dispatcher dictionary ──────────────────────────────────────────
_PROMPT_MODULES = {
    "Assamese": "assamese.py",
    "Bengali": "bengali.py",
    "Bodo": "bodo.py",
    "Dogri": "dogri.py",
    "Gujarati": "gujarati.py",
    "Hindi": "hindi.py",
    "Kannada": "kannada.py",
    "Kashmiri": "kashmiri.py",
    "Konkani": "konkani.py",
    "Malayalam": "malayalam.py",
    "Manipuri": "manipuri.py",
    "Marathi": "marathi.py",
    "Odia": "odia.py",
    "Punjabi": "punjabi.py",
    "Rajasthani": "rajasthani.py",
    "Sanskrit": "sanskrit.py",
    "Santhali": "santhali.py",
    "Sindhi": "sindhi.py",
    "Tamil": "tamil.py",
    "Telugu": "telugu.py",
    "Urdu": "urdu.py",
}

# ── Flexible key mapping for input files ────────────────────────────────────
ALTERNATIVE_KEY_MAP = {
    # poem_id variants
    "poem_id": "poem_id",
    "poem id": "poem_id",
    "Poem_ID": "poem_id",
    "Poem ID": "poem_id",
    "poemID": "poem_id",
    "id": "poem_id",

    # language variants
    "language": "language",
    "Language": "language",
    "lang": "language",

    # poem_title variants
    "poem_title": "poem_title",
    "poem title": "poem_title",
    "Poem_Title": "poem_title",
    "Poem Title": "poem_title",
    "title": "poem_title",

    # original_poem variants
    "original_poem": "original_poem",
    "original poem": "original_poem",
    "Original_Poem": "original_poem",
    "Original Poem": "original_poem",

    # translated_poem variants
    "translated_poem": "translated_poem",
    "translated poem": "translated_poem",
    "Translated_Poem": "translated_poem",
    "Translated Poem": "translated_poem",
}


def normalize_record_keys(record: dict) -> dict:
    """Rename known alternative keys to the expected ones."""
    normalized = {}
    for key, value in record.items():
        new_key = ALTERNATIVE_KEY_MAP.get(key, key)
        normalized[new_key] = value
    return normalized


def import_prompt_module(language: str):
    module_name = Path(_PROMPT_MODULES.get(language, "prompts_generic.py")).stem
    package_name = __package__ or "poem_annotator_fixed"
    return importlib.import_module(f"{package_name}.{module_name}")


def build_prompt_bundle_for_model(poem: PreprocessedPoem, model: str, semantic_context: dict) -> tuple[str, str, str]:
    module = import_prompt_module(poem.language)
    return module.build_prompt_bundle_for_model(poem, model, semantic_context)


def get_context(record: dict[str, str]) -> dict[str, Any]:
    # Semantic context generation is currently disabled to avoid optional IndicBERT dependencies.
    return {}


# ── Helper functions (unchanged) ─────────────────────────────────────────────
def resolve_api_token() -> str:
    env_token = os.getenv("LLM_PROXY_TOKEN", "").strip()
    if env_token:
        return env_token
    config_token = API_TOKEN.strip()
    if config_token and config_token != TOKEN_PLACEHOLDER:
        return config_token
    raise ValueError("Set LLM_PROXY_TOKEN or update API_TOKEN in config.py before running.")


def resolve_model_selection(selection: str | list[str]) -> list[str]:
    if selection == "all":
        return [m for m in MODEL_ORDER if m in PROXY_SUPPORTED_MODELS]
    if isinstance(selection, str):
        requested = [item.strip() for item in selection.split(",") if item.strip()]
    else:
        requested = [item.strip() for item in selection if item.strip()]
    invalid = [m for m in requested if m not in PROXY_SUPPORTED_MODELS]
    if invalid:
        raise ValueError(f"Unsupported model(s): {invalid}")
    selected = [m for m in MODEL_ORDER if m in requested]
    if not any(m in VOTING_MODELS for m in selected):
        raise ValueError("At least one of claude, gpt, or gemini must be selected.")
    return selected


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


def select_poems(
    dataset: list[dict[str, str]],
    poems_per_language: dict[str, int | str],
    *,
    poem_ids: list[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    id_filter = {pid.strip() for pid in (poem_ids or []) if pid.strip()}
    for record in dataset:
        if id_filter and record["poem_id"] not in id_filter:
            continue
        # ── Exclude specific poems ──
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


def determine_vote_basis(voting_sources: dict[str, str]) -> str:
    if set(voting_sources) >= {"claude", "gpt", "gemini"}:
        if voting_sources.get("gemini") == "gemini-3-flash":
            return "gemini_flash_fallback"
        return "full_3_vote"
    if len(voting_sources) == 2:
        return "reduced_2_vote"
    return "insufficient_vote_coverage"


def build_effective_voting_payloads(
    votes: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    effective: dict[str, dict[str, Any]] = {}
    sources: dict[str, str] = {}
    for model in ("claude", "gpt"):
        result = votes.get(model)
        if result and result["status"] == "valid" and result["parsed"] is not None:
            effective[model] = result["parsed"]
            sources[model] = model
    gemini_result = votes.get("gemini")
    if gemini_result and gemini_result["status"] == "valid" and gemini_result["parsed"] is not None:
        effective["gemini"] = gemini_result["parsed"]
        sources["gemini"] = "gemini"
    else:
        flash_result = votes.get("gemini-3-flash")
        if flash_result and flash_result["status"] == "valid" and flash_result["parsed"] is not None:
            effective["gemini"] = flash_result["parsed"]
            sources["gemini"] = "gemini-3-flash"
    return effective, sources


def is_output_current(output: dict[str, Any]) -> bool:
    if output.get("schema_version") != SCHEMA_VERSION or output.get("prompt_version") != PROMPT_VERSION:
        return False
    if "vote_basis" not in output:
        return False
    ann = output.get("annotation", {})
    if "translation_fidelity_score" not in ann:
        return False
    for stanza in ann.get("stanzas", []):
        if "scene" in stanza:
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
    return existing.get("agreement") != "pending"


# ── Load poems from a folder (with wrapper extraction) ──────────────────────
# ── Load poems from a folder (now filters unsupported languages) ─────────────
def load_poems_from_folder(folder_path: str | Path) -> list[dict[str, str]]:
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    all_records: list[dict[str, str]] = []
    for json_file in sorted(folder.glob("*.json")):
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "poems" in data and isinstance(data["poems"], list):
            items = data["poems"]
        elif isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = [data]
        else:
            print(f"Skipping {json_file}: not a recognised format", file=sys.stderr)
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            item = normalize_record_keys(item)

            # ── Check required keys ──
            missing = [k for k in REQUIRED_DATASET_KEYS if k not in item]
            if missing:
                print(f"Skipping record in {json_file.name}: missing keys {missing}", file=sys.stderr)
                continue

            # Ensure language field is present (if missing, guess from filename)
            if "language" not in item:
                stem = json_file.stem.lower()
                for lang in SUPPORTED_LANGUAGES:
                    if lang.lower() in stem:
                        item["language"] = lang
                        break
                if "language" not in item:
                    print(f"  Could not determine language for a record in {json_file.name}, skipping")
                    continue

            # ── Filter out unsupported languages ──
            if item["language"] not in SUPPORTED_LANGUAGES:
                continue   # silently skip Bodo, Konkani, etc.

            all_records.append(item)

    return all_records

# ── Core async processing (with per‑language output folders) ────────────────
async def process_poem(
    record: dict[str, str],
    *,
    selected_models: list[str],
    token: str,
    base_url: str,
    output_dir: Path,
    request_fn: Any = None,
) -> dict[str, Any]:
    poem = preprocess_poem(record)
    semantic_context = {}  # record.get("_semantic_context", {})
    out_path = output_path_for_poem(poem.poem_id, output_dir, language=poem.language)  # <-- language added
    if should_skip_output(out_path):
        return load_json_file(out_path)

    pending = build_pending_output(poem, selected_models)
    write_json_file(out_path, pending)

    primary_models = [m for m in selected_models if not (m == "gemini-3-flash" and "gemini" in selected_models)]
    tasks = []
    for model in primary_models:
        sys_prompt, user_prompt, repair_prompt = build_prompt_bundle_for_model(poem, model, semantic_context)
        tasks.append(fetch_model_vote(model, sys_prompt, user_prompt, repair_prompt, poem, token, base_url, request_fn=request_fn))
    results_list = await asyncio.gather(*tasks)
    votes = {model: result for model, result in zip(primary_models, results_list)}

    # Gemini flash fallback
    if "gemini" in selected_models and votes.get("gemini", {}).get("status") != "valid":
        sys_prompt, user_prompt, repair_prompt = build_prompt_bundle_for_model(poem, "gemini-3-flash", semantic_context)
        flash_vote = await fetch_model_vote("gemini-3-flash", sys_prompt, user_prompt, repair_prompt, poem, token, base_url, request_fn=request_fn)
        votes["gemini-3-flash"] = flash_vote
    elif "gemini-3-flash" in selected_models and "gemini-3-flash" not in votes:
        sys_prompt, user_prompt, repair_prompt = build_prompt_bundle_for_model(poem, "gemini-3-flash", semantic_context)
        flash_vote = await fetch_model_vote("gemini-3-flash", sys_prompt, user_prompt, repair_prompt, poem, token, base_url, request_fn=request_fn)
        votes["gemini-3-flash"] = flash_vote

    valid_payloads, voting_sources = build_effective_voting_payloads(votes)
    valid_model_count = sum(1 for v in votes.values() if v["status"] == "valid")
    vote_basis = determine_vote_basis(voting_sources)

    if len(valid_payloads) < 1:
        failed_output = pending | {"status": "failed", "_votes": votes, "vote_basis": vote_basis}
        failed_output["annotation"]["agreement_stats"]["valid_models_total"] = valid_model_count
        failed_output["annotation"]["agreement_stats"]["valid_voting_models"] = len(valid_payloads)
        failed_output["annotation"]["agreement_stats"]["vote_basis"] = vote_basis
        write_json_file(out_path, failed_output)
        return failed_output

    annotation, review_items, needs_review, poem_agreement = resolve_annotation(poem, valid_payloads, vote_basis=vote_basis)
    annotation["agreement_stats"]["selected_models"] = selected_models
    annotation["agreement_stats"]["valid_models_total"] = valid_model_count
    annotation["agreement_stats"]["valid_voting_models"] = len(valid_payloads)
    annotation["agreement_stats"]["vote_basis"] = vote_basis
    annotation["agreement_stats"]["effective_voting_sources"] = voting_sources

    completed = pending | {
        "status": "completed",
        "agreement": poem_agreement,
        "vote_basis": vote_basis,
        "needs_human_review": needs_review,
        "annotation": annotation,
        "review_items": review_items,
        "_votes": votes,
    }
    write_json_file(out_path, completed)
    return completed


async def run_pipeline(
    config: "RuntimeConfig",
    request_fn: Any = None,
) -> list[dict[str, Any]]:
    input_folder = Path(config.input_folder or "filtered_poems")
    output_dir = Path(config.output_dir or "output_small_batch")
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Load FAISS index once per run ---
    # build_faiss_index(term_file="cultural_terms.jsonl", index_file="cultural_index.faiss")
    
    token = resolve_api_token()

    all_results = []
    all_datasets = []

    for json_file in sorted(input_folder.glob("*.json")):
        dataset = load_dataset_file(json_file)
        # Remove excluded poems
        dataset = [p for p in dataset if p["poem_id"] not in EXCLUDED_POEM_IDS]
        # ── Extra safety: drop any poem whose language is not supported ──
        dataset = [p for p in dataset if p["language"] in SUPPORTED_LANGUAGES]

        selected_poems = select_poems(dataset, config.poems_per_language, poem_ids=config.poem_ids, limit=config.limit)

        results = []
        for record in selected_poems:
            record["_semantic_context"] = get_context(record)
            print(f"Processing poem {record['poem_id']} from {json_file.name} …")
            result = await process_poem(
                record,
                selected_models=config.selected_models,
                token=token,
                base_url=config.base_url,
                output_dir=output_dir,
                request_fn=request_fn,
            )
            results.append(result)
            print(f"  → {result.get('status', 'unknown')}")

        all_results.extend(results)
        all_datasets.extend(dataset)

    existing_outputs = collect_existing_outputs(all_datasets, output_dir)
    if config.write_summary:
        write_csv_rows(output_dir / SUMMARY_FILENAME, build_summary_rows(existing_outputs))
    if config.write_human_review_queue:
        write_csv_rows(output_dir / HUMAN_REVIEW_FILENAME, build_review_rows(existing_outputs))
    return all_results


def collect_existing_outputs(dataset: list[dict[str, str]], output_dir: Path) -> list[dict[str, Any]]:
    outputs = []
    for rec in dataset:
        path = output_path_for_poem(rec["poem_id"], output_dir, language=rec["language"])  # <-- language added
        if not path.exists():
            continue
        try:
            outputs.append(load_json_file(path))
        except (json.JSONDecodeError, OSError):
            continue
    return outputs


# ── Runtime configuration (unchanged) ────────────────────────────────────────
class RuntimeConfig:
    def __init__(self, dataset_path, selected_models, poems_per_language, concurrency,
                 poem_ids, limit, output_dir, write_summary, write_human_review_queue,
                 base_url, input_folder=None):
        self.dataset_path = dataset_path
        self.selected_models = selected_models
        self.poems_per_language = poems_per_language
        self.concurrency = concurrency
        self.poem_ids = poem_ids or []
        self.limit = limit
        self.output_dir = output_dir
        self.write_summary = write_summary
        self.write_human_review_queue = write_human_review_queue
        self.base_url = base_url
        self.input_folder = input_folder


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the poem annotation pipeline.")
    parser.add_argument("--dataset", help="Path to dataset.json file (default: dataset.json)")
    parser.add_argument("--input-folder", default="filtered_poems", help="Path to folder containing JSON files with poem records")
    parser.add_argument("--models", help="Comma-separated model list or 'all'.")
    parser.add_argument("--poems-per-language", nargs="*", default=[],
                        help="Overrides like Assamese=2 Bengali=all")
    parser.add_argument("--poem-id", action="append", default=[], help="Optional repeatable poem_id filter.")
    parser.add_argument("--limit", type=int, help="Optional cap after language filtering.")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--output-dir", default="output", help="Directory for per-language poem JSON outputs.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Proxy base URL override.")
    parser.add_argument("--no-summary", action="store_true", help="Skip annotation_summary.csv generation.")
    parser.add_argument("--no-human-review-queue", action="store_true", help="Skip human_review_queue.csv generation.")
    return parser.parse_args(argv)


def build_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    # Resolve dataset path (only needed if --input-folder is not used)
    dataset_path = None
    if args.input_folder:
        # If using input_folder, don't require dataset.json
        dataset_path = ""
    elif args.dataset:
        dataset_path = resolve_dataset_path(args.dataset)
    else:
        dataset_path = resolve_dataset_path(DATASET_PATH)
    
    selected_models = resolve_model_selection(args.models or "all")
    overrides = parse_language_overrides(args.poems_per_language)
    poems_per_language = merge_poem_limits(overrides)
    return RuntimeConfig(
        dataset_path=dataset_path,
        selected_models=selected_models,
        poems_per_language=poems_per_language,
        concurrency=args.concurrency,
        poem_ids=args.poem_id,
        limit=args.limit,
        output_dir=Path(args.output_dir),
        write_summary=not args.no_summary,
        write_human_review_queue=not args.no_human_review_queue,
        base_url=args.base_url,
        input_folder=args.input_folder,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_runtime_config(args)
        results = asyncio.run(run_pipeline(config))
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    completed = sum(1 for r in results if r.get("status") == "completed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    print(f"Processed {len(results)} poem(s): completed={completed}, failed={failed}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())