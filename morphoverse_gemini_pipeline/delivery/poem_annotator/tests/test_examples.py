"""CI gate: every language example is schema-valid, fully source-grounded,
and the built prompt is free of personas / forbidden tokens / visual_motifs.

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
FORBIDDEN = ["MorphoVerse", "scholar", "world expert", "gold annotator", "foremost", "visual_motifs"]


def _poem(text: str, language: str) -> PreprocessedPoem:
    stanzas, idx = [], 0
    for blk in re.split(r"\[STANZA \d+\]", text):
        src = re.search(r"SOURCE:\s*(.*)", blk)
        if not src:
            continue
        idx += 1
        s = [src.group(1).strip()] if src.group(1).strip() else []
        stanzas.append(StanzaInput(idx, len(s), s, []))
    original = "\n".join(" ".join(s.source_lines) for s in stanzas)
    return PreprocessedPoem("EX", "EX", language, original, "", stanzas,
                            len(stanzas), len(stanzas), "aligned", 1.0, "")


def _cases():
    for lang in LANGS:
        mod = importlib.import_module(f"poem_annotator.languages.{lang}")
        for n, ex in enumerate(getattr(mod, "EXAMPLES", []), 1):
            yield lang, n, ex


@pytest.mark.parametrize("lang,n,ex", list(_cases()))
def test_example_is_valid_and_grounded(lang, n, ex):
    poem = _poem(ex["input"], lang.capitalize())
    validated = validate_model_payload(ex["output"], poem)        # raises if schema-invalid
    gate = apply_source_term_gate(validated, poem)
    c = gate["source_term_checks"]
    assert c["entities_dropped"] == 0, f"{lang} ex{n} has ungrounded entity"
    assert c["metaphors_dropped"] == 0, f"{lang} ex{n} has ungrounded metaphor"
    # no POEM_ID / SEMANTIC_HINT leaked into the example input
    assert "POEM_ID" not in ex["input"] and "SEMANTIC_HINT" not in ex["input"]


def test_prompt_has_no_persona_or_forbidden_tokens():
    mod = importlib.import_module("poem_annotator.languages.hindi")
    if not mod.EXAMPLES:
        pytest.skip("no hindi examples")
    poem = _poem(mod.EXAMPLES[0]["input"], "Hindi")
    blob = "\n".join(build_prompt_bundle(poem, mod.EXAMPLES, mod.LANGUAGE_NOTE)).lower()
    for tok in FORBIDDEN:
        assert tok.lower() not in blob, f"prompt leaked forbidden token: {tok}"
