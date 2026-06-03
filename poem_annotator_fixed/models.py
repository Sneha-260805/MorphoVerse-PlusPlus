from __future__ import annotations

import json
import re
from typing import Any

from api import LLMProxyClient, LLMProxyError
from .config import REQUEST_MAX_TOKENS, REQUEST_TEMPERATURE, VOTING_MODELS
from .dataset import PreprocessedPoem


class ModelValidationError(ValueError):
    """Raised when a model response has the wrong schema."""


class StanzaCountMismatch(ModelValidationError):
    """Raised when a model response changes stanza segmentation."""


def extract_json_payload(raw_text: str) -> Any:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(stripped[start : end + 1])
        raise


def require_string(value: Any, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ModelValidationError(f"{field_name} must be a string")
    if not allow_empty and not value.strip():
        raise ModelValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_enum(value: Any, field_name: str, allowed: tuple[str, ...]) -> str:
    normalized = require_string(value, field_name)
    # Be tolerant of model casing, but normalize to the canonical enum value.
    allowed_lookup = {item.casefold(): item for item in allowed}
    key = normalized.casefold()
    if key not in allowed_lookup:
        raise ModelValidationError(f"{field_name} must be one of {list(allowed)}")
    return allowed_lookup[key]


def ensure_only_keys(obj: dict[str, Any], allowed_keys: set[str], field_name: str) -> None:
    extra_keys = sorted(set(obj) - allowed_keys)
    if extra_keys:
        raise ModelValidationError(f"{field_name} contains unexpected keys: {extra_keys}")


def validate_metaphor_spans(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ModelValidationError(f"{field_name} must be an array")
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ModelValidationError(f"{field_name}[{index}] must be an object")
        ensure_only_keys(item, {"source_term", "abstract_meaning"}, f"{field_name}[{index}]")
        source_term = require_string(item.get("source_term"), f"{field_name}[{index}].source_term")
        abstract_meaning = require_string(item.get("abstract_meaning"), f"{field_name}[{index}].abstract_meaning")
        normalized.append({"source_term": source_term, "abstract_meaning": abstract_meaning})
    return normalized


def validate_visual_motifs(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ModelValidationError(f"{field_name} must be an array")
    motifs: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        motif = require_string(item, f"{field_name}[{index}]")
        key = normalize_term(motif)
        if key and key not in seen:
            motifs.append(motif)
            seen.add(key)
    return motifs


def validate_model_payload(payload: Any, poem: PreprocessedPoem) -> dict[str, Any]:
    from .config import (
        ALLOWED_RECITATION_STYLES,
        ALLOWED_EMOTIONS,
        ALLOWED_TONES,
        ALLOWED_TRANSLATION_QUALITIES,
        ALLOWED_ENTITY_CATEGORIES,
    )

    if not isinstance(payload, dict):
        raise ModelValidationError("Model output must be a JSON object.")
    ensure_only_keys(payload, {"recitation_style", "emotional_arc", "stanzas", "cultural_entities"}, "payload")

    recitation_style = require_enum(payload.get("recitation_style"), "recitation_style", ALLOWED_RECITATION_STYLES)
    emotional_arc = require_string(payload.get("emotional_arc"), "emotional_arc", allow_empty=True)

    stanzas = payload.get("stanzas")
    if not isinstance(stanzas, list):
        raise ModelValidationError("stanzas must be a JSON array.")
    if len(stanzas) != len(poem.stanzas):
        raise StanzaCountMismatch(f"Expected {len(poem.stanzas)} stanzas but model returned {len(stanzas)}.")

    normalized_stanzas: list[dict[str, Any]] = []
    for i, stanza in enumerate(stanzas, start=1):
        if not isinstance(stanza, dict):
            raise ModelValidationError(f"stanzas[{i-1}] must be an object.")
        ensure_only_keys(
            stanza,
            {"index", "emotion", "tone", "translation_quality", "loss_note", "metaphor_spans", "visual_motifs"},
            f"stanzas[{i-1}]",
        )
        if stanza.get("index") != i:
            raise ModelValidationError(f"stanzas[{i-1}].index must be {i}")
        translation_quality = require_enum(
            stanza.get("translation_quality"),
            f"stanzas[{i-1}].translation_quality",
            ALLOWED_TRANSLATION_QUALITIES,
        )
        loss_note = require_string(stanza.get("loss_note"), f"stanzas[{i-1}].loss_note", allow_empty=True)
        if translation_quality == "faithful" and loss_note:
            raise ModelValidationError(f"stanzas[{i-1}].loss_note must be empty when translation_quality is faithful")

        metaphor_spans = validate_metaphor_spans(stanza.get("metaphor_spans", []), f"stanzas[{i-1}].metaphor_spans")
        visual_motifs = validate_visual_motifs(stanza.get("visual_motifs", []), f"stanzas[{i-1}].visual_motifs")

        normalized_stanzas.append({
            "index": i,
            "emotion": require_enum(stanza.get("emotion"), f"stanzas[{i-1}].emotion", ALLOWED_EMOTIONS),
            "tone": require_enum(stanza.get("tone"), f"stanzas[{i-1}].tone", ALLOWED_TONES),
            "translation_quality": translation_quality,
            "loss_note": loss_note,
            # IMPORTANT: keep these fields. The old version validated them but dropped them.
            "metaphor_spans": metaphor_spans,
            "visual_motifs": visual_motifs,
        })

    cultural_entities = payload.get("cultural_entities", [])
    if not isinstance(cultural_entities, list):
        raise ModelValidationError("cultural_entities must be a JSON array.")

    normalized_entities: list[dict[str, Any]] = []
    for j, entity in enumerate(cultural_entities):
        if not isinstance(entity, dict):
            raise ModelValidationError(f"cultural_entities[{j}] must be an object.")
        ensure_only_keys(
            entity,
            {"term", "romanization", "category", "stanza_index", "preserved", "translation_note"},
            f"cultural_entities[{j}]",
        )
        stanza_index_raw = entity.get("stanza_index", 1)
        try:
            stanza_index = int(stanza_index_raw)
        except (TypeError, ValueError):
            raise ModelValidationError(f"cultural_entities[{j}].stanza_index must be an integer.") from None
        if stanza_index < 1 or stanza_index > len(poem.stanzas):
            raise ModelValidationError(f"cultural_entities[{j}].stanza_index is out of range.")
        normalized_entities.append({
            "term": require_string(entity.get("term"), f"cultural_entities[{j}].term"),
            "romanization": require_string(entity.get("romanization"), f"cultural_entities[{j}].romanization", allow_empty=True),
            "category": require_enum(entity.get("category"), f"cultural_entities[{j}].category", ALLOWED_ENTITY_CATEGORIES),
            "stanza_index": stanza_index,
            "preserved": bool(entity.get("preserved")),
            "translation_note": require_string(entity.get("translation_note"), f"cultural_entities[{j}].translation_note", allow_empty=True),
        })

    return {
        "recitation_style": recitation_style,
        "emotional_arc": emotional_arc,
        "stanzas": normalized_stanzas,
        "cultural_entities": normalized_entities,
    }


def filter_non_cultural_entities(payload: dict[str, Any], language: str) -> dict[str, Any]:
    from .config import NON_CULTURAL_ENTITY_TERMS
    blocked_terms = {normalize_term(term) for term in NON_CULTURAL_ENTITY_TERMS.get(language, set())}
    if not blocked_terms:
        return payload

    filtered_entities = [entity for entity in payload["cultural_entities"] if normalize_term(entity["term"]) not in blocked_terms]
    return {**payload, "cultural_entities": filtered_entities}


def normalize_term(term: str) -> str:
    return re.sub(r"\s+", " ", term.strip()).casefold()


# ── API call wrapper ─────────────────────────────────────────────────────────
def call_model_text(model: str, system_prompt: str, user_prompt: str, token: str, base_url: str) -> str:
    client = LLMProxyClient(token=token, base_url=base_url)
    response = client.chat(
        model,
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=REQUEST_TEMPERATURE,
        max_tokens=REQUEST_MAX_TOKENS,
    )
    return response["choices"][0]["message"]["content"]


# ── Async fetch (voting) ─────────────────────────────────────────────────────
async def fetch_model_vote(
    model: str,
    system_prompt: str,
    primary_user_prompt: str,
    repair_user_prompt: str,
    poem: PreprocessedPoem,
    token: str,
    base_url: str,
    request_fn: Any = None,
) -> dict[str, Any]:
    import asyncio
    import inspect
    from .voting import build_comparison_payload

    request_func = request_fn or call_model_text
    last_raw_text = ""
    prompt_attempts = [("primary", primary_user_prompt), ("repair", repair_user_prompt)]
    for attempt_index, (prompt_kind, prompt_text) in enumerate(prompt_attempts):
        try:
            if request_fn is None:
                last_raw_text = await asyncio.to_thread(request_func, model, system_prompt, prompt_text, token, base_url)
            else:
                result = request_func(model, system_prompt, prompt_text, token, base_url)
                last_raw_text = await result if inspect.isawaitable(result) else result
        except LLMProxyError as exc:
            return {"status": "api_error", "retry_count": attempt_index, "raw_text": last_raw_text,
                    "parsed": None, "discard_reason": f"{exc.status_code} {exc.code}: {exc.message}",
                    "prompt_kind": prompt_kind,
                    "is_voting_model": model in VOTING_MODELS}
        except Exception as exc:
            return {"status": "request_error", "retry_count": attempt_index, "raw_text": last_raw_text,
                    "parsed": None, "discard_reason": str(exc),
                    "prompt_kind": prompt_kind,
                    "is_voting_model": model in VOTING_MODELS}

        try:
            parsed_json = extract_json_payload(last_raw_text)
        except json.JSONDecodeError as exc:
            if prompt_kind == "primary":
                continue
            return {"status": "parse_failed", "retry_count": attempt_index, "raw_text": last_raw_text,
                    "parsed": None, "discard_reason": f"JSON parse failed: {exc}",
                    "prompt_kind": prompt_kind,
                    "is_voting_model": model in VOTING_MODELS}

        try:
            validated = validate_model_payload(parsed_json, poem)
            validated = filter_non_cultural_entities(validated, poem.language)
        except StanzaCountMismatch as exc:
            return {"status": "stanza_mismatch", "retry_count": attempt_index, "raw_text": last_raw_text,
                    "parsed": None, "discard_reason": str(exc),
                    "prompt_kind": prompt_kind,
                    "is_voting_model": model in VOTING_MODELS}
        except ModelValidationError as exc:
            if prompt_kind == "primary":
                continue
            return {"status": "validation_failed", "retry_count": attempt_index, "raw_text": last_raw_text,
                    "parsed": None, "discard_reason": str(exc),
                    "prompt_kind": prompt_kind,
                    "is_voting_model": model in VOTING_MODELS}

        return {"status": "valid", "retry_count": attempt_index, "raw_text": last_raw_text,
                "parsed": validated, "discard_reason": "",
                "comparison": build_comparison_payload(validated),
                "prompt_kind": prompt_kind,
                "is_voting_model": model in VOTING_MODELS}

    return {"status": "parse_failed", "retry_count": 1, "raw_text": last_raw_text,
            "parsed": None, "discard_reason": "JSON parse/validation failed twice.",
            "prompt_kind": "repair",
            "is_voting_model": model in VOTING_MODELS}
