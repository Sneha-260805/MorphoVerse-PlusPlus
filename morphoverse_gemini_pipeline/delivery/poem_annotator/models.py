from __future__ import annotations

import json
import re
from typing import Any

from api import LLMProxyClient, LLMProxyError
from .config import REQUEST_TEMPERATURE, max_tokens_for, GEMINI_PRIMARY, GEMINI_FALLBACK
from .dataset import PreprocessedPoem
from .schema import (
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
    TOPLEVEL_KEYS,
    STANZA_KEYS,
    METAPHOR_KEYS,
    ENTITY_KEYS,
)


class ModelValidationError(ValueError):
    """Raised when a model response has the wrong schema."""


class StanzaCountMismatch(ModelValidationError):
    """Raised when a model response changes stanza segmentation."""


# ── Abbreviated key expansion ────────────────────────────────────────────────
def expand_abbreviated_keys(payload: Any) -> Any:
    """Expand abbreviated model output keys to full names before schema validation.

    The prompt asks the model to output compact keys (rs/ea/st/ce/i/em/to/tq/ln/ms
    etc.) to fit within the proxy's ~37-token completion cap.  This function
    expands them back to full field names so the rest of the pipeline is unchanged.
    Full-key dicts pass through unchanged (idempotent).
    """
    from .schema import ABBREV_TOPLEVEL, ABBREV_STANZA, ABBREV_METAPHOR, ABBREV_ENTITY
    if not isinstance(payload, dict):
        return payload
    expanded = {ABBREV_TOPLEVEL.get(k, k): v for k, v in payload.items()}
    stanzas = expanded.get("stanzas")
    if isinstance(stanzas, list):
        new_stanzas = []
        for st in stanzas:
            if not isinstance(st, dict):
                new_stanzas.append(st)
                continue
            exp_st = {ABBREV_STANZA.get(k, k): v for k, v in st.items()}
            spans = exp_st.get("metaphor_spans")
            if isinstance(spans, list):
                exp_st["metaphor_spans"] = [
                    {ABBREV_METAPHOR.get(k, k): v for k, v in m.items()}
                    if isinstance(m, dict) else m
                    for m in spans
                ]
            new_stanzas.append(exp_st)
        expanded["stanzas"] = new_stanzas
    entities = expanded.get("cultural_entities")
    if isinstance(entities, list):
        expanded["cultural_entities"] = [
            {ABBREV_ENTITY.get(k, k): v for k, v in e.items()}
            if isinstance(e, dict) else e
            for e in entities
        ]
    return expanded


# ── JSON extraction ──────────────────────────────────────────────────────────
def _repair_truncated_json(s: str) -> Any:
    """Best-effort repair of truncated JSON from proxy completion cutoff.

    Strategy (least to most invasive):
    1. Try a set of standard close-bracket suffixes.
    2. Trim up to 2000 chars from the right and retry suffixes.
    3. If cultural_entities is present but truncated, replace it with [].
    4. If stanzas is the truncated part, close it with format-aware suffixes.
    """
    if not s.startswith("{"):
        raise json.JSONDecodeError("not a JSON object", s, 0)

    generic_closings = [
        "",
        "}",
        "]}",
        "}]}",
        '"]}',
        '"}]}',
        '"}}]}',
    ]
    ce_closings = [
        '],"ce":[]}',
        '],"cultural_entities":[]}',
        '}],"ce":[]}',
        '}],"cultural_entities":[]}',
        '"}],"ce":[]}',
        '"}],"cultural_entities":[]}',
        '""}],"ce":[]}',
        '","ms":[]}],"ce":[]}',
        '[],"ms":[]}],"ce":[]}',
    ]
    all_closings = generic_closings + ce_closings

    for suffix in all_closings:
        try:
            result = json.loads(s + suffix)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Trim from the right (up to 2000 chars) until JSON closes cleanly.
    for trim in range(1, min(2000, len(s))):
        candidate = s[:-trim]
        for suffix in all_closings[1:]:
            try:
                result = json.loads(candidate + suffix)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

    # Structural recovery: if cultural_entities is truncated, replace with [].
    # Handles: {"recitation_style":...,"stanzas":[...],"cultural_entities":[{...cut
    ce_markers = ['"cultural_entities":', '"ce":']
    for marker in ce_markers:
        idx = s.rfind(marker)
        if idx != -1:
            truncated_at_ce = s[:idx] + '"cultural_entities":[]}'
            try:
                result = json.loads(truncated_at_ce)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

    raise json.JSONDecodeError("repair exhausted", s, 0)


def extract_json_payload(raw_text: str) -> Any:
    stripped = (raw_text or "").strip()
    if not stripped:
        raise json.JSONDecodeError("empty model response", "", 0)
    # Strip a leading/trailing code fence anywhere in the text (not only at the ends).
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        stripped = fence.group(1).strip() or stripped
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(stripped[start:end + 1])
            except json.JSONDecodeError:
                pass
        # Last resort: try to repair truncated JSON (proxy completion cutoff)
        candidate = stripped[start:] if start != -1 else stripped
        return _repair_truncated_json(candidate)


# ── Primitive validators ─────────────────────────────────────────────────────
def require_string(value: Any, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ModelValidationError(f"{field_name} must be a string")
    if not allow_empty and not value.strip():
        raise ModelValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_enum(value: Any, field_name: str, allowed: tuple[str, ...]) -> str:
    normalized = require_string(value, field_name)
    allowed_lookup = {item.casefold(): item for item in allowed}
    key = normalized.casefold()
    if key not in allowed_lookup:
        raise ModelValidationError(f"{field_name} must be one of {list(allowed)}")
    return allowed_lookup[key]


def ensure_only_keys(obj: dict[str, Any], allowed_keys: frozenset[str] | set[str], field_name: str) -> None:
    extra_keys = sorted(set(obj) - set(allowed_keys))
    if extra_keys:
        raise ModelValidationError(f"{field_name} contains unexpected keys: {extra_keys}")


def normalize_term(term: str) -> str:
    return re.sub(r"\s+", " ", term.strip()).casefold()


def coerce_to_text(value: Any) -> str:
    """Free-text fields (e.g. emotional_arc) may come back as a list or null.
    Normalize to a string instead of rejecting the whole annotation."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        parts = [str(v).strip() for v in value if str(v).strip()]
        return " → ".join(parts)
    return str(value).strip()


def _strip_ascii_gloss(term: str) -> str:
    """Remove trailing English gloss the model sometimes appends, e.g. ' (cold wind)'.
    Strips only ASCII-only parentheticals so Indic script in parens is untouched."""
    return re.sub(r"\s*\([A-Za-z0-9\s,\-']+\)\s*$", "", term).strip()


def term_in_source(term: str, source_text: str) -> bool:
    """Verbatim, whitespace-insensitive presence check (handles compounds/scripts).

    Also tries stripping trailing ASCII gloss the model sometimes appends to
    source_term (e.g. 'చల్లగా వీచే గాలి (cold wind)' → 'చల్లగా వీచే గాలి').
    """
    t = normalize_term(term)
    s = normalize_term(source_text)
    if t and t in s:
        return True
    if t and t.replace(" ", "") in s.replace(" ", ""):
        return True
    # Try after stripping any ASCII annotation gloss
    t2 = normalize_term(_strip_ascii_gloss(term))
    if t2 and t2 != t:
        if t2 in s:
            return True
        if t2.replace(" ", "") in s.replace(" ", ""):
            return True
    return False


# ── Metaphor span validation (no visual_motifs) ──────────────────────────────
def validate_metaphor_spans(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ModelValidationError(f"{field_name} must be an array")
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ModelValidationError(f"{field_name}[{index}] must be an object")
        ensure_only_keys(item, METAPHOR_KEYS, f"{field_name}[{index}]")
        source_term = require_string(item.get("source_term"), f"{field_name}[{index}].source_term")
        abstract_meaning = require_string(item.get("abstract_meaning"), f"{field_name}[{index}].abstract_meaning")
        normalized.append({"source_term": source_term, "abstract_meaning": abstract_meaning})
    return normalized


# ── Full schema validation ───────────────────────────────────────────────────
def validate_model_payload(payload: Any, poem: PreprocessedPoem) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ModelValidationError("Model output must be a JSON object.")
    ensure_only_keys(payload, TOPLEVEL_KEYS, "payload")

    recitation_style = require_enum(payload.get("recitation_style"), "recitation_style", ALLOWED_RECITATION_STYLES)
    emotional_arc = coerce_to_text(payload.get("emotional_arc"))

    stanzas = payload.get("stanzas")
    if not isinstance(stanzas, list):
        raise ModelValidationError("stanzas must be a JSON array.")
    if len(stanzas) != len(poem.stanzas):
        raise StanzaCountMismatch(f"Expected {len(poem.stanzas)} stanzas but model returned {len(stanzas)}.")

    normalized_stanzas: list[dict[str, Any]] = []
    for i, stanza in enumerate(stanzas, start=1):
        if not isinstance(stanza, dict):
            raise ModelValidationError(f"stanzas[{i-1}] must be an object.")
        ensure_only_keys(stanza, STANZA_KEYS, f"stanzas[{i-1}]")
        if stanza.get("index") != i:
            raise ModelValidationError(f"stanzas[{i-1}].index must be {i}")
        translation_quality = require_enum(
            stanza.get("translation_quality"), f"stanzas[{i-1}].translation_quality", ALLOWED_TRANSLATION_QUALITIES,
        )
        loss_note = require_string(stanza.get("loss_note"), f"stanzas[{i-1}].loss_note", allow_empty=True)
        if translation_quality == "faithful" and loss_note:
            raise ModelValidationError(f"stanzas[{i-1}].loss_note must be empty when translation_quality is faithful")
        metaphor_spans = validate_metaphor_spans(stanza.get("metaphor_spans", []), f"stanzas[{i-1}].metaphor_spans")
        normalized_stanzas.append({
            "index": i,
            "emotion": require_enum(stanza.get("emotion"), f"stanzas[{i-1}].emotion", ALLOWED_EMOTIONS),
            "tone": require_enum(stanza.get("tone"), f"stanzas[{i-1}].tone", ALLOWED_TONES),
            "translation_quality": translation_quality,
            "loss_note": loss_note,
            "metaphor_spans": metaphor_spans,
        })

    cultural_entities = payload.get("cultural_entities", [])
    if not isinstance(cultural_entities, list):
        raise ModelValidationError("cultural_entities must be a JSON array.")

    normalized_entities: list[dict[str, Any]] = []
    for j, entity in enumerate(cultural_entities):
        if not isinstance(entity, dict):
            raise ModelValidationError(f"cultural_entities[{j}] must be an object.")
        ensure_only_keys(entity, ENTITY_KEYS, f"cultural_entities[{j}]")
        stanza_index_raw = entity.get("stanza_index", 1)
        try:
            stanza_index = int(stanza_index_raw)
        except (TypeError, ValueError):
            raise ModelValidationError(f"cultural_entities[{j}].stanza_index must be an integer.") from None
        stanza_index = min(max(stanza_index, 1), len(poem.stanzas))
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
    blocked = {normalize_term(t) for t in NON_CULTURAL_ENTITY_TERMS.get(language, set())}
    if not blocked:
        return payload
    kept = [e for e in payload["cultural_entities"] if normalize_term(e["term"]) not in blocked]
    return {**payload, "cultural_entities": kept}


# ── Source-term evidence gate (Requirement 3) ────────────────────────────────
def apply_source_term_gate(payload: dict[str, Any], poem: PreprocessedPoem) -> dict[str, Any]:
    """Drop hallucinated terms; record what was dropped and which review items to raise."""
    source = poem.original_poem
    dropped_metaphors = 0
    dropped_entities = 0
    review_items: list[dict[str, Any]] = []

    new_stanzas = []
    for st in payload["stanzas"]:
        kept_spans = []
        for span in st["metaphor_spans"]:
            if term_in_source(span["source_term"], source):
                kept_spans.append(span)
            else:
                dropped_metaphors += 1
                review_items.append({
                    "field_path": f"annotation.stanzas[{st['index']}].metaphor_spans",
                    "severity": "low",
                    "resolved_value": "dropped",
                    "model_value": span["source_term"],
                    "note": "metaphor_source_term_not_in_source",
                })
        new_stanzas.append({**st, "metaphor_spans": kept_spans})

    kept_entities = []
    for ent in payload["cultural_entities"]:
        if term_in_source(ent["term"], source):
            kept_entities.append(ent)
        else:
            dropped_entities += 1
            review_items.append({
                "field_path": "annotation.cultural_entities",
                "severity": "medium",
                "resolved_value": "dropped",
                "model_value": ent["term"],
                "note": "entity_term_not_in_source",
            })

    gated = {**payload, "stanzas": new_stanzas, "cultural_entities": kept_entities}
    stats = {
        "entities_total": len(payload["cultural_entities"]),
        "entities_dropped": dropped_entities,
        "metaphors_total": sum(len(s["metaphor_spans"]) for s in payload["stanzas"]),
        "metaphors_dropped": dropped_metaphors,
    }
    return {"payload": gated, "source_term_checks": stats, "review_items": review_items}


# ── API call (Gemini only) ───────────────────────────────────────────────────
class EmptyModelResponse(RuntimeError):
    """Proxy returned HTTP 200 but with no text content (often throttling/quota)."""


def call_model_text(model: str, system_prompt: str, user_prompt: str, token: str,
                    base_url: str, *, max_tokens: int) -> str:
    client = LLMProxyClient(token=token, base_url=base_url)
    response = client.chat(
        model,
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=REQUEST_TEMPERATURE,
        max_tokens=max_tokens,
    )
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise EmptyModelResponse(f"malformed response shape: {exc}") from exc
    if not isinstance(content, str) or not content.strip():
        raise EmptyModelResponse("model returned empty content")
    return content


def _call_with_retries(request_func, model, system_prompt, prompt_text, token, base_url,
                       *, max_tokens, retries, base_delay):
    """Synchronous call wrapped in bounded exponential-backoff retries.
    Retries on empty responses and on transient proxy errors (429 / 5xx / network)."""
    import time

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            text = request_func(model, system_prompt, prompt_text, token, base_url, max_tokens=max_tokens)
            if not isinstance(text, str) or not text.strip():
                raise EmptyModelResponse("model returned empty content")
            return text
        except EmptyModelResponse as exc:
            last_exc = exc
        except LLMProxyError as exc:
            # Only retry transient statuses; re-raise hard auth/validation errors immediately.
            if exc.status_code in (0, 408, 409, 425, 429, 500, 502, 503, 504):
                last_exc = exc
            else:
                raise
        if attempt < retries:
            time.sleep(base_delay * (2 ** attempt))
    raise last_exc if last_exc else EmptyModelResponse("exhausted retries")


async def fetch_gemini_annotation(
    poem: PreprocessedPoem,
    system_prompt: str,
    primary_user_prompt: str,
    repair_user_prompt: str,
    token: str,
    base_url: str,
    request_fn: Any = None,
) -> dict[str, Any]:
    """Gemini-only: primary -> repair -> flash fallback. No voting."""
    import asyncio
    import inspect

    request_func = request_fn or call_model_text
    budget = max_tokens_for(len(poem.stanzas))
    last_raw = ""
    last_error = ""

    attempts = [
        (GEMINI_PRIMARY, primary_user_prompt, "primary"),
        (GEMINI_PRIMARY, repair_user_prompt, "repair"),
        (GEMINI_FALLBACK, repair_user_prompt, "flash_fallback"),
    ]

    for attempt_index, (model, prompt_text, kind) in enumerate(attempts):
        try:
            if request_fn is None:
                last_raw = await asyncio.to_thread(
                    _call_with_retries, request_func, model, system_prompt, prompt_text, token, base_url,
                    max_tokens=budget, retries=3, base_delay=2.0,
                )
            else:
                result = request_func(model, system_prompt, prompt_text, token, base_url, max_tokens=budget)
                last_raw = await result if inspect.isawaitable(result) else result
                if not isinstance(last_raw, str) or not last_raw.strip():
                    raise EmptyModelResponse("model returned empty content")
        except EmptyModelResponse as exc:
            last_error = f"empty_response: {exc}"
            if kind != "flash_fallback":
                continue
            return _fail("empty_response", attempt_index, last_raw or "", last_error, model, kind)
        except LLMProxyError as exc:
            last_error = f"{exc.status_code} {exc.code}: {exc.message}"
            if kind != "flash_fallback":
                continue
            return _fail("api_error", attempt_index, last_raw or "", last_error, model, kind)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if kind != "flash_fallback":
                continue
            return _fail("request_error", attempt_index, last_raw or "", last_error, model, kind)

        try:
            parsed = expand_abbreviated_keys(extract_json_payload(last_raw))
        except json.JSONDecodeError as exc:
            if kind != "flash_fallback":
                continue
            return _fail("parse_failed", attempt_index, last_raw, f"JSON parse failed: {exc}", model, kind)

        try:
            validated = validate_model_payload(parsed, poem)
            validated = filter_non_cultural_entities(validated, poem.language)
        except StanzaCountMismatch as exc:
            if kind != "flash_fallback":
                continue
            return _fail("stanza_mismatch", attempt_index, last_raw, str(exc), model, kind)
        except ModelValidationError as exc:
            if kind != "flash_fallback":
                continue
            return _fail("validation_failed", attempt_index, last_raw, str(exc), model, kind)

        return {"status": "valid", "model": model, "prompt_kind": kind,
                "retry_count": attempt_index, "raw_text": last_raw,
                "parsed": validated, "discard_reason": ""}

    return _fail("empty_response", len(attempts) - 1, last_raw or "",
                 last_error or "All Gemini attempts returned empty/invalid output.", GEMINI_FALLBACK, "flash_fallback")


def _fail(status: str, attempt: int, raw: str, reason: str, model: str, kind: str) -> dict[str, Any]:
    return {"status": status, "model": model, "prompt_kind": kind,
            "retry_count": attempt, "raw_text": raw, "parsed": None, "discard_reason": reason}
