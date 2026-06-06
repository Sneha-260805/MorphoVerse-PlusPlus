"""CI gate: every language example is schema-valid, fully source-grounded,
and the built prompt is free of truly forbidden tokens.

Run:  pytest -q
"""
import importlib
import json
import re
from pathlib import Path

import pytest

from poem_annotator.dataset import PreprocessedPoem, StanzaInput
from poem_annotator.models import validate_model_payload, apply_source_term_gate, ModelValidationError
from poem_annotator.shared_prompt_builder import build_prompt_bundle

LANG_DIR = Path(__file__).resolve().parent.parent / "languages"
LANGS = sorted(p.stem for p in LANG_DIR.glob("*.py")
               if p.stem not in {"__init__", "generic"})
FORBIDDEN = ["foremost"]


def _poem(text: str, language: str) -> PreprocessedPoem:
    stanzas, idx = [], 0
    for blk in re.split(r"\[STANZA \d+\]", text):
        # Capture SOURCE: until the next keyword (TRANSLATION/SEMANTIC_HINT/[STANZA)
        src_match = re.search(r"SOURCE:\s*(.*?)(?=\nTRANSLATION:|\nSEMANTIC_HINT:|\[STANZA|\Z)",
                              blk, flags=re.DOTALL)
        if not src_match:
            continue
        idx += 1
        raw_src = src_match.group(1).strip()
        # Collect all non-empty lines from the source block
        s = [ln.strip() for ln in raw_src.splitlines() if ln.strip()]
        stanzas.append(StanzaInput(idx, len(s), s, []))
    original = "\n".join(" ".join(st.source_lines) for st in stanzas)
    return PreprocessedPoem("EX", "EX", language, original, "", stanzas,
                            len(stanzas), len(stanzas), "aligned", 1.0, "")


def _cases():
    for lang in LANGS:
        mod = importlib.import_module(f"poem_annotator.languages.{lang}")
        # New files use LANG_EXAMPLES (e.g. HINDI_EXAMPLES); fall back to EXAMPLES.
        lang_var = lang.upper() + "_EXAMPLES"
        examples = getattr(mod, lang_var, None) or getattr(mod, "EXAMPLES", [])
        for n, ex in enumerate(examples, 1):
            yield lang, n, ex


@pytest.mark.parametrize("lang,n,ex", list(_cases()))
def test_example_is_valid_and_grounded(lang, n, ex):
    poem = _poem(ex["input"], lang.capitalize())
    # Handle both dict and JSON-string output formats
    raw_output = ex["output"]
    output = raw_output if isinstance(raw_output, dict) else json.loads(raw_output)
    validated = validate_model_payload(output, poem)
    gate = apply_source_term_gate(validated, poem)
    c = gate["source_term_checks"]
    assert c["entities_dropped"] == 0, f"{lang} ex{n} has ungrounded entity"
    assert c["metaphors_dropped"] == 0, f"{lang} ex{n} has ungrounded metaphor"


def test_prompt_has_no_forbidden_tokens():
    mod = importlib.import_module("poem_annotator.languages.hindi")
    if not hasattr(mod, "build_prompt_bundle_for_model"):
        pytest.skip("hindi module missing build_prompt_bundle_for_model")
    if not getattr(mod, "HINDI_EXAMPLES", None):
        pytest.skip("no hindi examples")
    from poem_annotator.dataset import PreprocessedPoem, StanzaInput
    poem = _poem(mod.HINDI_EXAMPLES[0]["input"], "Hindi")
    system, user, repair = mod.build_prompt_bundle_for_model(poem, "claude", {})
    blob = "\n".join([system, user, repair]).lower()
    for tok in FORBIDDEN:
        assert tok.lower() not in blob, f"prompt leaked forbidden token: {tok}"
