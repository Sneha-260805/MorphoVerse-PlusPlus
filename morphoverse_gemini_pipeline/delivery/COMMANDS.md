# MorphoVerse++ → Gemini-Only Pipeline — Commands & Migration Guide

This package is the fully refactored codebase. Layout:

```
api.py                              # reference proxy client (replace with yours if you have one)
requirements.txt
poem_annotator/
├── __init__.py
├── schema.py                       # canonical schema — single source of truth
├── config.py                       # Gemini-only, MAX_OUTPUT_TOKENS, alignment thresholds
├── alignment.py                    # stanza alignment confidence
├── dataset.py                      # preprocessing + alignment integration
├── models.py                       # schema + source-term validation, Gemini call path
├── assemble.py                     # single-model assembly (replaces voting.py)
├── shared_prompt_builder.py        # ONE neutral prompt for all languages
├── output.py                       # canonical output + CSVs (no visual_motifs)
├── main.py                         # Gemini-only orchestration
├── indic_bert_context.py           # advisory hints only (off by default)
├── languages/                      # DATA ONLY: EXAMPLES + LANGUAGE_NOTE per language
│   ├── hindi.py … urdu.py (21)     # telugu.py is an empty stub — add examples
│   └── generic.py                  # fallback
└── tests/test_examples.py          # CI gate
```

Removed from the old tree: `voting.py` (replaced by `assemble.py`), all per-language
templates/builders/personas (languages are now data-only), and every `visual_motifs`
reference except the intentional stale-output guard in `main.py:is_output_current`.

---

## 1. Setup

```bash
# from the folder that CONTAINS api.py and poem_annotator/
python -m venv .venv && source .venv/bin/activate          # optional
pip install -r requirements.txt

export LLM_PROXY_TOKEN="your-token-here"                    # REQUIRED (no token is committed)
# optional, heavy: enable semantic stanza alignment (needs torch + sentence-transformers)
# export USE_SEMANTIC_ALIGNMENT=1
```

## 2. Run the pipeline

```bash
# annotate a folder of poem JSON files (each {"poems":[...]} or a bare list)
python -m poem_annotator.main \
    --input-folder filtered_poems \
    --output-dir output \
    --poems-per-language Hindi=3 Telugu=all

# single poem
python -m poem_annotator.main --input-folder filtered_poems --poem-id MV++_0477

# outputs:
#   output/<Language>/<poem_id>.json
#   output/annotation_summary.csv
#   output/human_review_queue.csv
```

Completed poems are skipped on re-run only if they are at schema_version=5 / prompt_version=6
AND contain no legacy `visual_motifs`/`scene` fields — so all prior outputs auto-recompute.

## 3. CI gates (run after any edit to examples or schema)

```bash
# (a) example correctness + prompt cleanliness
python -m pytest poem_annotator/tests -q

# (b) no active visual_motifs usage (the guard line is the only allowed mention)
grep -rnE 'visual_motifs"|\.visual_motifs|visual_motifs *=' poem_annotator --include='*.py' \
  | grep -v 'is_output_current\|"visual_motifs" in stanza' \
  && { echo "FAIL: stray visual_motifs"; exit 1; } || echo "PASS"

# (c) no voting / persona machinery resurfaced
grep -rniE 'majority_vote|VOTING_MODELS|MODEL_ORDER|resolve_categorical|MorphoVerse|foremost scholar' \
  poem_annotator --include='*.py' | grep -v '# ' \
  && { echo "FAIL"; exit 1; } || echo "PASS"
```

## 4. Add the missing Telugu examples

`languages/telugu.py` is an empty stub (the source file was not provided). Add 3–5 examples
in the same shape as the others, then re-run the CI gate:

```python
# languages/telugu.py
import json
LANGUAGE_NOTE = ""
EXAMPLES = json.loads(r"""
[
  {"input": "LANGUAGE: Telugu\nSTANZA_COUNT: 1\nSTANZAS:\n[STANZA 1]\nSOURCE: <telugu line>\nTRANSLATION: <english>",
   "output": {"recitation_style":"reflective","emotional_arc":"peace",
              "stanzas":[{"index":1,"emotion":"peace","tone":"wonder","translation_quality":"faithful","loss_note":"","metaphor_spans":[]}],
              "cultural_entities":[]}}
]
""")
```
The CI gate will reject any example whose `term`/`source_term` is not verbatim in its own SOURCE.

---

## What changed vs. the requirements

1. Few-shot examples rewritten/cleaned (POEM_ID + SEMANTIC_HINT stripped, visual_motifs removed,
   ungrounded entities/metaphors dropped — 13 ungrounded entities + 1 metaphor were removed from the
   shipped examples by the source-term gate).
2. Personas removed; one neutral system prompt in `shared_prompt_builder.py`.
3. Hard source-term validation in `models.apply_source_term_gate` (drop + review; salvage status).
4. Robust alignment in `alignment.align_stanzas` (count/length/semantic → `alignment_risk`).
5. Correct single-model handling: no `majority_vote`; confidence derived from evidence; review forced.
6. `MAX_OUTPUT_TOKENS=4096` + dynamic `max_tokens_for(stanza_count)`.
7. Shared prompt builder; languages are data-only.
8. `visual_motifs` removed everywhere except the stale-output guard.
9. Gemini-only: primary → repair → `gemini-3-flash` fallback; no Claude/GPT, no voting.

## Known follow-ups (need your judgment / data)
- Telugu examples (stub).
- Verbatim matching can over-drop inflected Indic forms (e.g. lemma `राम` vs. inflected `रामं`);
  entities are routed to review, but tune `term_in_source` if false drops appear on real data.
- Calibrate `ALIGN_OK`/`ALIGN_RISK` and the `confidence_label` thresholds against a human-labeled
  sample before trusting `confidence:"high"` downstream.
