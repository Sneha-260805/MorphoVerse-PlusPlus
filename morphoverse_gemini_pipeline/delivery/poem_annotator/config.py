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

# ── Model selection ──────────────────────────────────────────────────────────
# Claude is the primary model: the proxy's Gemini endpoint has a hard completion
# cap of ~38 tokens which truncates any annotation JSON, causing all outputs to
# fail validation.  The Claude endpoint (claude-sonnet-4-6 via proxy id "claude")
# returns full completions (361+ tokens observed).
GEMINI_PRIMARY = "claude"            # legacy one-shot path model id (only used when USE_CHUNKED_GEMINI=False)
GEMINI_FALLBACK = "gemini-3-flash"   # repair / fallback; kept as-is for retries

# ── Chunked Gemini annotation (Gemini-only) ──────────────────────────────────
# The proxy's Gemini upstreams (gemini-3.1-pro-preview / gemini-3-flash-preview)
# are thinking models with a hidden ~960-token thinking cap we cannot configure,
# so a one-shot annotation prompt truncates to empty output. The chunked path
# (poem_annotator/gemini_chunked.py) splits each poem into small single-purpose
# calls (pro first, flash fallback) so each stays under the cap. This keeps the
# pipeline Gemini-only with NO Claude/OpenAI involvement.
USE_CHUNKED_GEMINI = os.getenv("USE_CHUNKED_GEMINI", "1") == "1"
# (MODEL_ORDER and VOTING_MODELS intentionally removed — no multi-model voting.)

# ── Generation defaults ──────────────────────────────────────────────────────
REQUEST_TEMPERATURE = 0.1
# R1 fix: 1000 truncated long-poem JSON. Use a generous floor and scale by stanza count.
MAX_OUTPUT_TOKENS = 4096


def max_tokens_for(stanza_count: int) -> int:
    # Indic script metaphor_spans and cultural entity terms are token-expensive.
    # Observed: 3-stanza Punjabi annotation = 1624+ tokens (finish_reason=length).
    # Raise base to 1536 and per-stanza step to 300; cap at 2048 (proxy limit).
    return max(1536, min(2048, 1536 + 300 * max(stanza_count - 1, 0)))


# ── Alignment thresholds ─────────────────────────────────────────────────────
ALIGN_OK = 0.75            # >= this and equal counts -> "aligned"
ALIGN_RISK = 0.60          # < this -> "alignment_risk"
ALIGN_PAIR_COSINE_MIN = 0.45
USE_SEMANTIC_ALIGNMENT = os.getenv("USE_SEMANTIC_ALIGNMENT", "0") == "1"  # off by default (heavy dep)

# ── Output settings ──────────────────────────────────────────────────────────
SUMMARY_FILENAME = "annotation_summary.csv"
HUMAN_REVIEW_FILENAME = "human_review_queue.csv"
SCHEMA_VERSION = 5
PROMPT_VERSION = 9  # Gemini-only chunked annotation (gemini-3.1-pro + gemini-3-flash fallback); replaces claude one-shot

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
