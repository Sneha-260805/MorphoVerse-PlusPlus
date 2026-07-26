"""Exact substring location for source_span_* fields (never invent spans)."""
from __future__ import annotations

import re
import unicodedata


def _normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text.strip())).casefold()


def find_exact_substring(needle: str, haystack: str) -> str | None:
    """Return the exact haystack substring matching needle, or None if not found."""
    if not needle or not haystack:
        return None

    needle_nfc = unicodedata.normalize("NFC", needle)
    haystack_nfc = unicodedata.normalize("NFC", haystack)

    idx = haystack_nfc.find(needle_nfc)
    if idx >= 0:
        return haystack_nfc[idx : idx + len(needle_nfc)]

    # Whitespace-insensitive contiguous match
    n_norm = _normalize_for_match(needle_nfc)
    if not n_norm:
        return None

    # Build char map from normalized haystack positions to original indices
    orig_chars: list[str] = []
    norm_to_orig_start: list[int] = []
    buf = ""
    for i, ch in enumerate(haystack_nfc):
        if ch.isspace():
            if buf and not buf.endswith(" "):
                buf += " "
            continue
        buf += ch.casefold()
        orig_chars.append(ch)
        norm_to_orig_start.append(i)

    norm_hay = buf.strip()
    pos = norm_hay.find(n_norm.replace(" ", ""))
    if pos < 0:
        pos = norm_hay.find(n_norm)
    if pos < 0:
        return None

    # Map back approximately: find first orig index whose casefold prefix aligns
    target = n_norm.replace(" ", "")
    compact_hay = norm_hay.replace(" ", "")
    cpos = compact_hay.find(target)
    if cpos < 0:
        return None

    # Walk original to find span covering target length in compact form
    compact_idx = 0
    start_orig: int | None = None
    end_orig: int | None = None
    for i, ch in enumerate(haystack_nfc):
        if ch.isspace():
            continue
        if compact_idx == cpos and start_orig is None:
            start_orig = i
        compact_idx += 1
        if start_orig is not None and compact_idx == cpos + len(target):
            end_orig = i + 1
            break
    if start_orig is not None and end_orig is not None:
        return haystack_nfc[start_orig:end_orig]
    return None


def find_translation_span(
    *,
    term: str,
    romanization: str,
    translation_note: str,
    translated_poem: str,
    preserved: bool,
) -> str | None:
    """Best-effort exact translation substring; None if not confidently found."""
    candidates: list[str] = []
    if translation_note:
        # Quoted fragments in notes
        for m in re.finditer(r"'([^']{3,80})'|\"([^\"]{3,80})\"", translation_note):
            candidates.append(m.group(1) or m.group(2) or "")
        # Longest ASCII phrase in note
        ascii_bits = re.findall(r"[A-Za-z][A-Za-z0-9\s,\-']{2,80}", translation_note)
        candidates.extend(sorted(ascii_bits, key=len, reverse=True))
    if romanization and preserved:
        candidates.append(romanization)

    seen: set[str] = set()
    for cand in candidates:
        cand = cand.strip()
        if len(cand) < 3 or cand in seen:
            continue
        seen.add(cand)
        span = find_exact_substring(cand, translated_poem)
        if span:
            return span
    return None
