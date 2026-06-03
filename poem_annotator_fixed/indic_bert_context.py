"""Semantic grounding module using IndicBERT + FAISS retrieval."""

import json
import os
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

# ── Model caching (load once per process) ────────────────────────────────────
_tokenizer = None
_model = None
_sentence_model = None        # for sentence embeddings (optional)
_faiss_index = None            # FAISS index for cultural term retrieval
_term_list = []                # list of terms in the same order as index
_term_categories = []          # parallel list of categories

def load_models():
    global _tokenizer, _model, _sentence_model
    if _tokenizer is None:
        model_name = "ai4bharat/IndicBERTv2-MLM-only"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModel.from_pretrained(model_name)
        _model.eval()
    if _sentence_model is None:
        # LaBSE for sentence‑level similarity (better cross‑lingual)
        _sentence_model = SentenceTransformer("sentence-transformers/LaBSE")

def get_embedding(text: str) -> np.ndarray:
    load_models()
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = _model(**inputs)
    # mean pooling over token embeddings (exclude special tokens)
    mask = inputs["attention_mask"]
    token_embeddings = outputs.last_hidden_state
    input_mask_expanded = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return (sum_embeddings / sum_mask).squeeze().cpu().numpy()

def get_sentence_embedding(text: str) -> np.ndarray:
    """Higher‑quality sentence embedding for similarity tasks."""
    load_models()
    return _sentence_model.encode(text, normalize_embeddings=True)

# ── Simple label mapping (can be replaced with trained classifiers) ────────
EMOTION_LIST = ["grief", "longing", "devotion", "peace", "celebration", "resilience", "anger", "fear"]
THEME_LIST   = ["Nature", "Love Romance", "Philosophy", "Celebration Joy", "Grief Loss",
                "Patriotism", "Resilience", "Devotion", "Social Justice"]

def classify_by_prototype(embedding: np.ndarray, candidates: list[str], prototype_vectors: dict[str, np.ndarray]) -> tuple[str, float]:
    """Return the candidate whose prototype has highest cosine similarity."""
    best, best_sim = "", -1.0
    for cand in candidates:
        proto = prototype_vectors.get(cand)
        if proto is None:
            continue
        sim = np.dot(embedding, proto) / (np.linalg.norm(embedding) * np.linalg.norm(proto))
        if sim > best_sim:
            best_sim = sim
            best = cand
    return best, best_sim

# ── Pre‑compute prototype embeddings for emotion/theme (first call) ────────
_emotion_prototypes = {}
_theme_prototypes   = {}
_prototypes_initialized = False

def init_prototypes():
    global _emotion_prototypes, _theme_prototypes, _prototypes_initialized
    if _prototypes_initialized:
        return
    # These are very simple prototypes – for a real system you'd average many examples
    proto_texts_emotion = {
        "grief": "deep sorrow and pain, loss, weeping, mourning, absence",
        "longing": "yearning desire, nostalgia, missing someone or something, waiting",
        "devotion": "worship, reverence, dedication, prayer, sacred love",
        "peace": "calm, serenity, stillness, contentment, harmony",
        "celebration": "joy, happiness, festivity, triumph, exultation",
        "resilience": "strength, perseverance, endurance, overcoming, determination",
        "anger": "rage, fury, indignation, protest, rebellion",
        "fear": "dread, terror, anxiety, fright, insecurity",
    }
    proto_texts_theme = {
        "Nature": "trees, rivers, mountains, rain, flowers, sky",
        "Love Romance": "beloved, passion, heart, union, beauty",
        "Philosophy": "existence, meaning, truth, knowledge, consciousness",
        "Celebration Joy": "festival, happiness, triumph, dancing, singing",
        "Grief Loss": "sorrow, separation, death, lament, mourning",
        "Patriotism": "homeland, soil, nation, freedom, sacrifice",
        "Resilience": "strength, courage, endurance, hope, overcoming",
        "Devotion": "god, prayer, temple, sacred, worship, divine",
        "Social Justice": "equality, oppression, rights, justice, struggle",
    }
    for label, text in proto_texts_emotion.items():
        _emotion_prototypes[label] = get_sentence_embedding(text)
    for label, text in proto_texts_theme.items():
        _theme_prototypes[label] = get_sentence_embedding(text)
    _prototypes_initialized = True

# ── Cultural term retrieval (FAISS index) ───────────────────────────────────
def build_faiss_index(term_file: str = "cultural_terms.jsonl", index_file: str = "cultural_index.faiss"):
    """Build a FAISS index from a JSONL file containing lines like:
    {"term": "गंगा", "category": "SACRED_RIVER", "description": "The most sacred river in Hinduism"}
    Save the index and metadata to disk for later use."""
    import faiss
    global _faiss_index, _term_list, _term_categories
    if os.path.exists(index_file):
        _faiss_index = faiss.read_index(index_file)
        _term_list, _term_categories = load_term_list(term_file)
        return

    terms = []
    categories = []
    embeddings = []
    with open(term_file, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            term = obj["term"]
            cat = obj.get("category", "")
            desc = obj.get("description", term)
            terms.append(term)
            categories.append(cat)
            # embed the description for a richer representation
            emb = get_sentence_embedding(desc)
            embeddings.append(emb)

    embeddings = np.array(embeddings, dtype=np.float32)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # inner product = cosine for normalized vectors
    index.add(embeddings)
    faiss.write_index(index, index_file)
    with open(term_file + ".terms", "w", encoding="utf-8") as f:
        json.dump({"terms": terms, "categories": categories}, f)
    _faiss_index = index
    _term_list = terms
    _term_categories = categories

def load_term_list(term_file: str):
    path = term_file + ".terms"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["terms"], data["categories"]
    # fallback: make an empty list
    return [], []

def retrieve_cultural_terms(query_embedding: np.ndarray, top_k: int = 5, threshold: float = 0.6) -> list[tuple[str, str, float]]:
    """Given an embedding, return top‑k similar cultural terms with their categories."""
    if _faiss_index is None or len(_term_list) == 0:
        return []
    query = np.array([query_embedding], dtype=np.float32)
    scores, indices = _faiss_index.search(query, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score < threshold:
            continue
        results.append((_term_list[idx], _term_categories[idx], float(score)))
    return results

# ── Main context generator ──────────────────────────────────────────────────
def get_context(poem_record: dict) -> dict:
    """Produce a rich semantic_context dict for a poem record.
    The record must have keys: 'original_poem', 'translated_poem' (and optionally 'language').
    """
    init_prototypes()

    original = poem_record.get("original_poem", "")
    translated = poem_record.get("translated_poem", "")
    full_text = original + "\n" + translated

    # poem‑level embedding
    emb_full = get_sentence_embedding(full_text)

    # emotion & theme by prototype similarity
    emotion_label, emotion_conf = classify_by_prototype(emb_full, EMOTION_LIST, _emotion_prototypes)
    theme_label, theme_conf = classify_by_prototype(emb_full, THEME_LIST, _theme_prototypes)

    # emotional arc: single word for now; could be expanded to stanza‑level later
    suggested_emotional_arc = emotion_label if emotion_label else "unknown"

    # cultural terms via retrieval (if index loaded)
    likely_terms = retrieve_cultural_terms(emb_full, top_k=5)
    likely_cultural_terms = [{"term": t, "category": c} for t, c, _ in likely_terms]

    # metaphor likelihood per stanza (placeholder – can be refined with stanza boundaries)
    # Here we just flag the whole poem as having some metaphorical density if any term similarity is high.
    metaphor_probability = 0.0
    if _faiss_index:
        # rough: if we retrieved strongly, it's likely more metaphorical
        metaphor_probability = min(1.0, len(likely_terms) / 5.0)

    # translation alignment score (cosine similarity between original and translation emb)
    orig_emb = get_sentence_embedding(original) if original else np.zeros(768)  # dimension depends on model
    trans_emb = get_sentence_embedding(translated) if translated else orig_emb
    if np.linalg.norm(orig_emb) > 0 and np.linalg.norm(trans_emb) > 0:
        tr_align = float(np.dot(orig_emb, trans_emb) / (np.linalg.norm(orig_emb) * np.linalg.norm(trans_emb)))
    else:
        tr_align = 1.0

    # devotional probability: prototype of "devotion" phrase
    devo_text = "devotion worship prayer divine sacred"
    devo_emb = get_sentence_embedding(devo_text)
    devo_prob = float(np.dot(emb_full, devo_emb)) if np.linalg.norm(emb_full) > 0 else 0.0

    return {
        "suggested_emotional_arc": suggested_emotional_arc,
        "suggested_theme": theme_label if theme_label else "unknown",
        "likely_cultural_terms": likely_cultural_terms,
        "metaphor_probability": round(metaphor_probability, 3),
        "translation_alignment_score": round(tr_align, 3),
        "devotional_probability": round(devo_prob, 3),
        "language_is_low_resource": poem_record.get("language") in {"Santhali", "Bodo", "Konkani", "Manipuri"},
    }