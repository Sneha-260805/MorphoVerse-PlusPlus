"""MorphoVerse++ Schema v1.1 validation (backward-compatible with v5 readers)."""
from __future__ import annotations

from typing import Any

from .models import ModelValidationError, require_enum, require_string, ensure_only_keys
from .schema import (
    ALLOWED_VISUAL_PRIORITIES,
    ALLOWED_EXPRESSION_TYPES,
    ALLOWED_CULTURAL_SPECIFICITY_LEVELS,
    ALLOWED_VISUALIZATION_DIFFICULTY,
    ENTITY_KEYS_V1_1,
    ENTITY_OPTIONAL_PILOT_KEYS,
    METAPHOR_KEYS_V1_1,
    ANNOTATION_OPTIONAL_PILOT_KEYS,
    SCHEMA_VERSION_V1_1,
)
from .span_utils import find_exact_substring


def _optional_enum(value: Any, field: str, allowed: tuple[str, ...]) -> str | None:
    if value is None or value == "":
        return None
    return require_enum(value, field, allowed)


def validate_span_in_text(span: str | None, text: str, field_name: str) -> str | None:
    if span is None or span == "":
        return None
    if not isinstance(span, str):
        raise ModelValidationError(f"{field_name} must be a string or null")
    exact = find_exact_substring(span, text)
    if exact is None:
        raise ModelValidationError(f"{field_name} is not an exact substring of the poem text")
    return exact


def validate_metaphor_v1_1(item: dict[str, Any], index: int, *, original_poem: str) -> dict[str, Any]:
    allowed = set(METAPHOR_KEYS_V1_1)
    extra = set(item) - allowed
    if extra:
        raise ModelValidationError(f"metaphor_spans[{index}] unexpected keys: {sorted(extra)}")
    for key in ("source_term", "abstract_meaning", "expression_type"):
        if key not in item:
            raise ModelValidationError(f"metaphor_spans[{index}] missing {key}")

    source_term = require_string(item["source_term"], f"metaphor_spans[{index}].source_term")
    if find_exact_substring(source_term, original_poem) is None:
        raise ModelValidationError(f"metaphor_spans[{index}].source_term not found in original poem")

    expression_type = require_enum(
        item["expression_type"], f"metaphor_spans[{index}].expression_type", ALLOWED_EXPRESSION_TYPES,
    )
    literal = item.get("literal_meaning")
    mapping = item.get("metaphor_mapping")
    literal_out = None if literal in (None, "") else require_string(literal, f"metaphor_spans[{index}].literal_meaning")
    mapping_out = None if mapping in (None, "") else require_string(mapping, f"metaphor_spans[{index}].metaphor_mapping")

    if expression_type == "other" and not literal_out and not mapping_out:
        pass  # allowed
    if expression_type in ("metaphor", "simile", "symbolism") and mapping_out is None and literal_out is None:
        pass  # nullable per policy

    return {
        "source_term": source_term,
        "abstract_meaning": require_string(item["abstract_meaning"], f"metaphor_spans[{index}].abstract_meaning"),
        "expression_type": expression_type,
        "literal_meaning": literal_out,
        "metaphor_mapping": mapping_out,
    }


def validate_entity_v1_1(
    item: dict[str, Any],
    index: int,
    *,
    original_poem: str,
    translated_poem: str,
) -> dict[str, Any]:
    allowed = set(ENTITY_KEYS_V1_1) | ENTITY_OPTIONAL_PILOT_KEYS
    extra = set(item) - allowed
    if extra:
        raise ModelValidationError(f"cultural_entities[{index}] unexpected keys: {sorted(extra)}")

    out: dict[str, Any] = {
        "term": require_string(item["term"], f"cultural_entities[{index}].term"),
        "romanization": require_string(item.get("romanization", ""), f"cultural_entities[{index}].romanization", allow_empty=True),
        "category": item["category"],
        "stanza_index": int(item["stanza_index"]),
        "preserved": bool(item.get("preserved")),
        "translation_note": require_string(item.get("translation_note", ""), f"cultural_entities[{index}].translation_note", allow_empty=True),
        "visual_priority": require_enum(
            item["visual_priority"], f"cultural_entities[{index}].visual_priority", ALLOWED_VISUAL_PRIORITIES,
        ),
        "acceptable_visual_variants": _validate_variant_list(item.get("acceptable_visual_variants"), index),
        "source_span_original": validate_span_in_text(item.get("source_span_original"), original_poem, f"cultural_entities[{index}].source_span_original"),
        "source_span_translation": validate_span_in_text(item.get("source_span_translation"), translated_poem, f"cultural_entities[{index}].source_span_translation"),
    }
    out["cultural_specificity_level"] = _optional_enum(
        item.get("cultural_specificity_level"), f"cultural_entities[{index}].cultural_specificity_level",
        ALLOWED_CULTURAL_SPECIFICITY_LEVELS,
    )
    out["visualization_difficulty"] = _optional_enum(
        item.get("visualization_difficulty"), f"cultural_entities[{index}].visualization_difficulty",
        ALLOWED_VISUALIZATION_DIFFICULTY,
    )
    return out


def _validate_variant_list(value: Any, index: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ModelValidationError(f"cultural_entities[{index}].acceptable_visual_variants must be a list")
    out: list[str] = []
    for j, v in enumerate(value):
        out.append(require_string(v, f"cultural_entities[{index}].acceptable_visual_variants[{j}]"))
    return out


def validate_v1_1_output(output: dict[str, Any]) -> list[str]:
    """Validate a full v1.1 poem output. Returns list of error strings (empty = ok)."""
    errors: list[str] = []
    if output.get("schema_version") != SCHEMA_VERSION_V1_1:
        errors.append(f"schema_version must be {SCHEMA_VERSION_V1_1!r}")

    original = output.get("original_poem", "")
    translated = output.get("translated_poem", "")
    ann = output.get("annotation") or {}

    for key in ANNOTATION_OPTIONAL_PILOT_KEYS:
        if key in ann and ann[key] not in (None, ""):
            try:
                if key == "cultural_specificity_level":
                    _optional_enum(ann[key], f"annotation.{key}", ALLOWED_CULTURAL_SPECIFICITY_LEVELS)
                else:
                    _optional_enum(ann[key], f"annotation.{key}", ALLOWED_VISUALIZATION_DIFFICULTY)
            except ModelValidationError as exc:
                errors.append(str(exc))

    try:
        for i, st in enumerate(ann.get("stanzas") or []):
            for j, m in enumerate(st.get("metaphor_spans") or []):
                validate_metaphor_v1_1(m, j, original_poem=original)
        for i, ent in enumerate(ann.get("cultural_entities") or []):
            validate_entity_v1_1(ent, i, original_poem=original, translated_poem=translated)
    except ModelValidationError as exc:
        errors.append(str(exc))

    return errors
