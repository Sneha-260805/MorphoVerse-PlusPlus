from __future__ import annotations

import os

# Re-export the canonical enums so legacy `from .config import ALLOWED_*` keeps working.
from .schema import (  # noqa: F401
    ALLOWED_RECITATION_STYLES,
    ALLOWED_EMOTIONS,
    ALLOWED_TONES,
    ALLOWED_TRANSLATION_QUALITIES,
    ALLOWED_ENTITY_CATEGORIES,
)

# ── Dataset & authentication ─────────────────────────────────────────────────
DATASET_PATH = "dataset.json"
API_TOKEN = os.getenv("LLM_PROXY_TOKEN", "").strip()
DEFAULT_BASE_URL = "https://llmproxy.magnocode.tech"
TOKEN_PLACEHOLDER = "<SET_YOUR_TOKEN_HERE>"

# ── Model selection (GEMINI ONLY) ────────────────────────────────────────────
GEMINI_PRIMARY = "gemini"            # main annotation model (proxy id)
GEMINI_FALLBACK = "gemini-3-flash"   # repair / fallback model only
# (MODEL_ORDER and VOTING_MODELS intentionally removed — no multi-model voting.)

# ── Generation defaults ──────────────────────────────────────────────────────
REQUEST_TEMPERATURE = 0.1
# R1 fix: 1000 truncated long-poem JSON. Use a generous floor and scale by stanza count.
MAX_OUTPUT_TOKENS = 4096


def max_tokens_for(stanza_count: int) -> int:
    """Dynamic budget so long poems do not get truncated mid-array."""
    return max(1500, min(8192, 800 + 300 * max(stanza_count, 1)))


# ── Alignment thresholds ─────────────────────────────────────────────────────
ALIGN_OK = 0.75            # >= this and equal counts -> "aligned"
ALIGN_RISK = 0.60          # < this -> "alignment_risk"
ALIGN_PAIR_COSINE_MIN = 0.45
USE_SEMANTIC_ALIGNMENT = os.getenv("USE_SEMANTIC_ALIGNMENT", "0") == "1"  # off by default (heavy dep)

# ── Output settings ──────────────────────────────────────────────────────────
SUMMARY_FILENAME = "annotation_summary.csv"
HUMAN_REVIEW_FILENAME = "human_review_queue.csv"
SCHEMA_VERSION = 5
PROMPT_VERSION = 6

# ── Non-cultural entity filters ──────────────────────────────────────────────
NON_CULTURAL_ENTITY_TERMS: dict[str, set[str]] = {
    "Telugu": {"వసంత ఋతువు"},
}

# ── Required dataset keys ────────────────────────────────────────────────────
REQUIRED_DATASET_KEYS = (
    "language", "poem_id", "poem_title", "original_poem", "translated_poem",
)

# ── Supported languages ──────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "Assamese", "Bengali", "Bodo", "Dogri", "Gujarati", "Hindi", "Kannada",
    "Kashmiri", "Konkani", "Malayalam", "Manipuri", "Marathi", "Odia",
    "Punjabi", "Rajasthani", "Sanskrit", "Santhali", "Sindhi", "Tamil",
    "Telugu", "Urdu",
}

# ── Default poem limits (per language) ──────────────────────────────────────
DEFAULT_POEMS_PER_LANGUAGE: dict[str, int] = {
    "Assamese": 5,
    "Bengali": 5,
    "Hindi": 5,
    "Marathi": 5,
    "Telugu": 5,
}
