from __future__ import annotations

from collections import defaultdict
from typing import Any

from .config import VOTING_MODELS
from .dataset import PreprocessedPoem
from .models import normalize_term


TRANSLATION_SCORE = {
    "faithful": 1.0,
    "partial": 0.5,
    "lost": 0.0,
}


def build_comparison_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact payload for debugging/model comparison."""
    return {
        "recitation_style": payload["recitation_style"],
        "stanzas": [
            {
                "index": s["index"],
                "emotion": s["emotion"],
                "tone": s["tone"],
                "translation_quality": s["translation_quality"],
                "metaphor_terms": [m.get("source_term", "") for m in s.get("metaphor_spans", [])],
                "visual_motifs": s.get("visual_motifs", []),
            }
            for s in payload["stanzas"]
        ],
        "cultural_entities": [
            {"term": normalize_term(e["term"]), "category": e["category"], "preserved": bool(e["preserved"])}
            for e in payload["cultural_entities"]
        ],
    }


def choose_preferred_model(models: set[str], preference_order: tuple[str, ...] = VOTING_MODELS) -> str | None:
    for model in preference_order:
        if model in models:
            return model
    return next(iter(models), None)


def agreement_from_top_count(top_count: int, valid_count: int) -> str:
    if valid_count >= 3:
        if top_count >= 3:
            return "high"
        if top_count == 2:
            return "medium"
        return "low"
    if valid_count == 2:
        return "medium" if top_count == 2 else "low"
    return "low"


def _normalize_vote_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.casefold()
    if isinstance(value, bool):
        return bool(value)
    return value


def resolve_categorical_field(
    field_name: str,
    model_values: dict[str, Any],
    *,
    preference_order: tuple[str, ...] = VOTING_MODELS,
) -> dict[str, Any]:
    """Resolve categorical value while preserving canonical/raw value from chosen model.

    Old bug: this returned the casefolded group key, converting DEITY -> deity.
    """
    valid_models = [model for model in preference_order if model in model_values]
    if not valid_models:
        return {"value": "", "agreement": "low", "source_model": None, "resolution_basis": "no_valid_vote"}

    grouped: dict[Any, list[str]] = defaultdict(list)
    for model in valid_models:
        grouped[_normalize_vote_value(model_values[model])].append(model)

    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), min(preference_order.index(m) for m in item[1])))
    _winning_group_key, winning_models = ranked[0]
    chosen_model = choose_preferred_model(set(winning_models), preference_order)
    valid_count = len(valid_models)
    agreement = agreement_from_top_count(len(winning_models), valid_count)

    resolution_basis = "majority_vote"
    if valid_count == 2 and len(ranked) == 2 and len(winning_models) == 1:
        resolution_basis = "claude_tiebreak_no_third_vote" if chosen_model == "claude" else "preferred_model_tiebreak_no_third_vote"
    elif valid_count == 2:
        resolution_basis = "reduced_2_vote"
    elif valid_count >= 3 and len(winning_models) >= 3:
        resolution_basis = "full_3_vote_unanimous"

    return {
        "value": model_values[chosen_model] if chosen_model else model_values[winning_models[0]],
        "agreement": agreement,
        "source_model": chosen_model,
        "resolution_basis": resolution_basis,
    }


def resolve_free_text_field(model_values: dict[str, str]) -> dict[str, Any]:
    preferred = choose_preferred_model(set(model_values.keys()), VOTING_MODELS)
    if preferred is None:
        return {"value": "", "agreement": "low", "source_model": None, "resolution_basis": "no_valid_vote"}
    return {
        "value": model_values[preferred],
        "agreement": "medium" if preferred == "claude" else "low",
        "source_model": preferred,
        "resolution_basis": "claude_free_text" if preferred == "claude" else "fallback_free_text",
    }


def build_review_item(field_path: str, agreement: str, resolved_value: Any, model_values: dict[str, Any], *, note: str = "") -> dict[str, Any]:
    return {
        "field_path": field_path,
        "agreement": agreement,
        "resolved_value": resolved_value,
        "claude_value": model_values.get("claude", ""),
        "gpt_value": model_values.get("gpt", ""),
        "gemini_value": model_values.get("gemini", ""),
        "note": note,
    }


def _term_appears_in_source(term: str, poem: PreprocessedPoem) -> bool:
    term_norm = normalize_term(term)
    source_norm = normalize_term(poem.original_poem)
    if term_norm and term_norm in source_norm:
        return True
    # Also try a whitespace-free check for compounds/scripts.
    compact_term = term_norm.replace(" ", "")
    compact_source = source_norm.replace(" ", "")
    return bool(compact_term and compact_term in compact_source)


def _has_explicit_deity_vote(per_model_entities: dict[str, dict[str, Any]], poem: PreprocessedPoem) -> bool:
    for entity in per_model_entities.values():
        if entity.get("category") == "DEITY" and _term_appears_in_source(entity.get("term", ""), poem):
            return True
    return False


def resolve_cultural_entities(
    valid_payloads: dict[str, dict[str, Any]],
    poem: PreprocessedPoem,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, bool]:
    review_items: list[dict[str, Any]] = []
    resolved_entities: list[dict[str, Any]] = []
    low_entity_count = 0
    forced_human_review = False

    entity_votes: dict[str, dict[str, dict[str, Any]]] = {}
    for model in VOTING_MODELS:
        payload = valid_payloads.get(model)
        if not payload:
            continue
        for entity in payload["cultural_entities"]:
            key = normalize_term(entity["term"])
            if not key:
                continue
            entity_votes.setdefault(key, {})[model] = entity

    valid_models = [model for model in VOTING_MODELS if model in valid_payloads]
    valid_count = len(valid_models)

    for _key, per_model_entities in entity_votes.items():
        presence_count = len(per_model_entities)
        presence_agreement = agreement_from_top_count(presence_count, valid_count)
        explicit_deity = _has_explicit_deity_vote(per_model_entities, poem)
        include_entity = presence_count > (valid_count / 2) or explicit_deity

        term_values = {model: entity["term"] for model, entity in per_model_entities.items()}
        displayed_term = next(iter(term_values.values()))
        if presence_agreement == "low" or not include_entity or explicit_deity and presence_count <= (valid_count / 2):
            low_entity_count += 1
            review_items.append(build_review_item(
                f"annotation.cultural_entities[{displayed_term}].presence",
                "low" if presence_agreement == "low" else presence_agreement,
                "included" if include_entity else "excluded",
                {model: ("present" if model in per_model_entities else "absent") for model in VOTING_MODELS},
                note=f"presence_count={presence_count}/{valid_count}" + ("; explicit_deity_preserved" if explicit_deity else ""),
            ))
            if explicit_deity:
                forced_human_review = True
        if not include_entity and valid_count == 2 and presence_count == 1:
            forced_human_review = True

        if not include_entity:
            continue

        canonical_model = choose_preferred_model(set(per_model_entities.keys()), VOTING_MODELS)
        canonical_entity = per_model_entities[canonical_model] if canonical_model else next(iter(per_model_entities.values()))

        category_res = resolve_categorical_field("category", {model: e["category"] for model, e in per_model_entities.items()})
        preserved_res = resolve_categorical_field("preserved", {model: e["preserved"] for model, e in per_model_entities.items()})
        romanization_res = resolve_free_text_field({model: e["romanization"] for model, e in per_model_entities.items()})
        translation_note_res = resolve_free_text_field({model: e["translation_note"] for model, e in per_model_entities.items()})

        if category_res["agreement"] == "low":
            low_entity_count += 1
            review_items.append(build_review_item(
                f"annotation.cultural_entities[{canonical_entity['term']}].category",
                "low", category_res["value"],
                {model: e["category"] for model, e in per_model_entities.items()},
                note=category_res["resolution_basis"],
            ))
            forced_human_review = True
        if preserved_res["agreement"] == "low":
            low_entity_count += 1
            review_items.append(build_review_item(
                f"annotation.cultural_entities[{canonical_entity['term']}].preserved",
                "low", preserved_res["value"],
                {model: e["preserved"] for model, e in per_model_entities.items()},
                note=preserved_res["resolution_basis"],
            ))
            forced_human_review = True

        stanza_index = min(max(int(canonical_entity["stanza_index"]), 1), len(poem.stanzas))
        resolved_entities.append({
            "term": canonical_entity["term"],
            "romanization": romanization_res,
            "category": category_res,
            "stanza_index": stanza_index,
            "preserved": preserved_res,
            "translation_note": translation_note_res,
            "presence_agreement": presence_agreement,
        })

    return resolved_entities, review_items, low_entity_count, forced_human_review


def resolve_stanza_metaphor_and_motifs(
    stanza_votes: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Combine stanza-level metaphor_spans and visual_motifs across models."""
    valid_models = [model for model in VOTING_MODELS if model in stanza_votes]
    valid_count = len(valid_models)

    # Metaphors: dedupe by source_term, keep preferred model's meaning, report agreement.
    term_models: dict[str, list[str]] = {}
    term_payloads: dict[str, dict[str, dict[str, str]]] = {}
    for model in valid_models:
        for span in stanza_votes[model].get("metaphor_spans", []):
            term = span.get("source_term", "")
            if not term:
                continue
            norm_term = normalize_term(term)
            term_models.setdefault(norm_term, []).append(model)
            term_payloads.setdefault(norm_term, {})[model] = span

    resolved_metaphors: list[dict[str, Any]] = []
    for norm_term, models in term_models.items():
        chosen_model = choose_preferred_model(set(models), VOTING_MODELS)
        chosen_span = term_payloads[norm_term][chosen_model]
        resolved_metaphors.append({
            "source_term": chosen_span.get("source_term", norm_term),
            "abstract_meaning": chosen_span.get("abstract_meaning", ""),
            "agreement": agreement_from_top_count(len(set(models)), valid_count),
            "source_model": chosen_model,
        })

    # Motifs: dedupe by normalized motif, keep preferred model's original string, report agreement.
    motif_models: dict[str, list[str]] = {}
    motif_strings: dict[str, dict[str, str]] = {}
    for model in valid_models:
        for motif in stanza_votes[model].get("visual_motifs", []):
            if not isinstance(motif, str) or not motif.strip():
                continue
            norm = normalize_term(motif)
            motif_models.setdefault(norm, []).append(model)
            motif_strings.setdefault(norm, {})[model] = motif.strip()

    resolved_motifs: list[dict[str, Any]] = []
    for norm, models in sorted(motif_models.items()):
        chosen_model = choose_preferred_model(set(models), VOTING_MODELS)
        motif = motif_strings[norm][chosen_model]
        resolved_motifs.append({
            "motif": motif,
            "agreement": agreement_from_top_count(len(set(models)), valid_count),
            "source_model": chosen_model,
        })

    return resolved_metaphors, resolved_motifs


def _motif_review_needed(motifs: list[dict[str, Any]]) -> bool:
    """Flag obviously fragmented motif lists without blocking output."""
    weak_singletons = {"eye", "eyes", "face", "hand", "hands", "feet", "foot", "lotus", "flower"}
    weak_count = sum(1 for item in motifs if normalize_term(item.get("motif", "")) in weak_singletons)
    return weak_count >= 3


def resolve_annotation(
    poem: PreprocessedPoem,
    valid_payloads: dict[str, dict[str, Any]],
    *,
    vote_basis: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], bool, str]:
    review_items: list[dict[str, Any]] = []
    categorical_agreements: list[str] = []
    forced_human_review = False

    recitation_style = resolve_categorical_field("recitation_style", {m: p["recitation_style"] for m, p in valid_payloads.items()})
    emotional_arc = resolve_free_text_field({m: p["emotional_arc"] for m, p in valid_payloads.items()})
    categorical_agreements.append(recitation_style["agreement"])
    if recitation_style["agreement"] == "low":
        review_items.append(build_review_item(
            "annotation.recitation_style", "low", recitation_style["value"],
            {m: p["recitation_style"] for m, p in valid_payloads.items()},
            note=recitation_style["resolution_basis"],
        ))
        forced_human_review = True

    resolved_stanzas: list[dict[str, Any]] = []
    low_stanza_count = 0
    medium_stanza_count = 0
    fidelity_sum = 0.0

    for stanza in poem.stanzas:
        svotes = {m: p["stanzas"][stanza.stanza_index - 1] for m, p in valid_payloads.items()}
        emotion = resolve_categorical_field("emotion", {m: v["emotion"] for m, v in svotes.items()})
        tone = resolve_categorical_field("tone", {m: v["tone"] for m, v in svotes.items()})
        tq = resolve_categorical_field("translation_quality", {m: v["translation_quality"] for m, v in svotes.items()})
        loss_note = resolve_free_text_field({m: v["loss_note"] for m, v in svotes.items()})
        metaphors, motifs = resolve_stanza_metaphor_and_motifs(svotes)

        categorical_agreements.extend([emotion["agreement"], tone["agreement"], tq["agreement"]])
        stanza_is_low = emotion["agreement"] == "low" or tone["agreement"] == "low" or tq["agreement"] == "low"
        if stanza_is_low:
            low_stanza_count += 1
        elif "medium" in (emotion["agreement"], tone["agreement"], tq["agreement"]):
            medium_stanza_count += 1

        for field_name, resolved in (("emotion", emotion), ("tone", tone), ("translation_quality", tq)):
            if resolved["agreement"] == "low":
                review_items.append(build_review_item(
                    f"annotation.stanzas[{stanza.stanza_index}].{field_name}",
                    "low", resolved["value"],
                    {m: v[field_name] for m, v in svotes.items()},
                    note=resolved["resolution_basis"],
                ))
                forced_human_review = True

        if tq["value"] == "faithful":
            loss_note = {"value": "", "agreement": "high", "source_model": None, "resolution_basis": "blanked_for_faithful_quality"}
        fidelity_sum += TRANSLATION_SCORE.get(tq["value"], 0.0)

        if _motif_review_needed(motifs):
            review_items.append(build_review_item(
                f"annotation.stanzas[{stanza.stanza_index}].visual_motifs",
                "low",
                [m["motif"] for m in motifs],
                {model: svotes[model].get("visual_motifs", []) for model in VOTING_MODELS if model in svotes},
                note="possible_fragmented_visual_motifs",
            ))
            forced_human_review = True

        resolved_stanzas.append({
            "stanza_index": stanza.stanza_index,
            "line_count": stanza.line_count,
            "source_lines": stanza.source_lines,
            "translated_lines": stanza.translated_lines,
            "emotion": emotion,
            "tone": tone,
            "translation_quality": tq,
            "loss_note": loss_note,
            "metaphor_spans": metaphors,
            "visual_motifs": motifs,
        })

    resolved_entities, entity_review, low_entity, entity_forced = resolve_cultural_entities(valid_payloads, poem)
    review_items.extend(entity_review)
    for entity in resolved_entities:
        categorical_agreements.append(entity["presence_agreement"])
        categorical_agreements.append(entity["category"]["agreement"])
        categorical_agreements.append(entity["preserved"]["agreement"])

    translation_fidelity_score = fidelity_sum / max(len(poem.stanzas), 1)
    needs_human_review = (
        low_stanza_count > len(poem.stanzas) / 2
        or low_entity > 0
        or forced_human_review
        or entity_forced
    )

    if needs_human_review or any(a == "low" for a in categorical_agreements):
        poem_agreement = "low"
    elif any(a == "medium" for a in categorical_agreements):
        poem_agreement = "medium"
    else:
        poem_agreement = "high"

    annotation = {
        "recitation_style": recitation_style,
        "emotional_arc": emotional_arc,
        "translation_fidelity_score": round(translation_fidelity_score, 6),
        "stanzas": resolved_stanzas,
        "cultural_entities": resolved_entities,
        "agreement_stats": {
            "selected_models": list(VOTING_MODELS),
            "voting_models": list(VOTING_MODELS),
            "valid_voting_models": len(valid_payloads),
            "low_stanza_count": low_stanza_count,
            "medium_stanza_count": medium_stanza_count,
            "low_entity_count": low_entity,
            "review_item_count": len(review_items),
            "vote_basis": vote_basis,
        },
    }
    return annotation, review_items, needs_human_review, poem_agreement
