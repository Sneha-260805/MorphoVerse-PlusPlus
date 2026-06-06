"""Add emotional_arc length rule to COMMON_RULES in all 21 language files."""
from pathlib import Path

LANGS_DIR = Path("poem_annotator/languages")

OLD = '13. Use [] for metaphor_spans when none are clearly supported.\n14. Visual motifs are NOT required; do NOT output any visual_motifs field.'
NEW = '13. Use [] for metaphor_spans when none are clearly supported.\n14. Visual motifs are NOT required; do NOT output any visual_motifs field.\n15. emotional_arc must be a concise phrase of max 8 words (e.g. "grief to peace", "longing through devotion").'

# Also handle variant with en-dash instead of hyphen
OLD2 = '13. Use [] for metaphor_spans when none are clearly supported.\n14. Visual motifs are NOT required; do NOT output any visual_motifs field.'

updated = []
for f in sorted(LANGS_DIR.glob("*.py")):
    if f.stem in ("__init__", "generic"):
        continue
    text = f.read_text(encoding="utf-8")
    if "emotional_arc must be a concise" in text:
        continue  # already patched
    if OLD in text:
        new_text = text.replace(OLD, NEW, 1)
        f.write_text(new_text, encoding="utf-8")
        updated.append(f.name)
    # try with en-dash (some files use ‑ instead of -)
    elif "13." in text and "14." in text:
        # find end of rule 14 line and insert rule 15
        import re
        pat = r'(14\. Visual motifs are NOT required.*?\n)'
        m = re.search(pat, text)
        if m:
            insert_pos = m.end()
            new_text = text[:insert_pos] + '15. emotional_arc must be a concise phrase of max 8 words (e.g. "grief to peace", "longing through devotion").\n' + text[insert_pos:]
            f.write_text(new_text, encoding="utf-8")
            updated.append(f.name)

print(f"Updated {len(updated)} files: {', '.join(updated)}")
