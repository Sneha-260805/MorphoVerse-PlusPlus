"""Debug: map out proxy behavior for annotation prompts.
Key question: finish_reason and why annotation JSON is truncated.
"""
import sys, os, json
sys.path.insert(0, ".")
os.environ["LLM_PROXY_TOKEN"] = "7467da865bd89ad904e68bf1de7141a749e6d569d65c62a2"
os.environ["PYTHONIOENCODING"] = "utf-8"

from api import LLMProxyClient, LLMProxyError
from poem_annotator.dataset import load_dataset_file, preprocess_poem
from poem_annotator.main import _load_language_data
from poem_annotator.shared_prompt_builder import build_prompt_bundle as bpb, SYSTEM_PROMPT
from pathlib import Path

TOKEN = "7467da865bd89ad904e68bf1de7141a749e6d569d65c62a2"
BASE_URL = "https://llmproxy.magnocode.tech"

records = load_dataset_file(Path("morphoverse_jsons/assamese_poems.json"))
poem_record = next(r for r in records if r["poem_id"] == "MV++_0003")
poem = preprocess_poem(poem_record)
examples, note = _load_language_data(poem.language)
system_prompt, user_prompt, repair_prompt = bpb(poem, examples, note, semantic_context={})

c = LLMProxyClient(token=TOKEN, base_url=BASE_URL)


def call_and_show(label, model, messages, budget):
    try:
        raw = c.chat(model, messages, max_tokens=budget, temperature=0.1)
        ch = (raw.get("choices") or [{}])[0]
        content = ch.get("message", {}).get("content", "") or ""
        finish = ch.get("finish_reason", "?")
        usage = raw.get("usage", {})
        print(f"[{label}] max={budget}: len={len(content)} finish={finish} | usage={usage}")
        if content:
            print(f"  content: {repr(content[:200])}")
        return content, finish
    except LLMProxyError as e:
        print(f"[{label}] max={budget}: HTTP {e.status_code} {e.code}")
        return "", "error"
    except Exception as e:
        print(f"[{label}] max={budget}: ERROR {e}")
        return "", "error"


# ── TEST 1: Full prompt with finish_reason ─────────────────────────────────────
print("=== TEST 1: Full annotation prompt (800 input tokens) ===")
msgs_full = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
for budget in [512, 768, 1024, 1280, 1536]:
    call_and_show("gemini/full", "gemini", msgs_full, budget)

# ── TEST 2: NO examples (strip examples block) ────────────────────────────────
print()
print("=== TEST 2: NO-examples prompt ===")
# Build prompt without examples
no_ex_user = user_prompt.replace(
    user_prompt[user_prompt.find("EXAMPLES (schema reference):"):],
    "Return the JSON object now."
).strip() + "\nReturn the JSON object now."

print(f"No-examples prompt: {len(no_ex_user)} chars")
msgs_noex = [{"role": "system", "content": system_prompt}, {"role": "user", "content": no_ex_user}]
for budget in [512, 768, 1024, 1536, 2048]:
    call_and_show("gemini/noex", "gemini", msgs_noex, budget)

# ── TEST 3: Ultra-minimal prompt ──────────────────────────────────────────────
print()
print("=== TEST 3: Ultra-minimal prompt (Assamese source, no rules, no examples) ===")
src_lines = " | ".join(" | ".join(s.source_lines) for s in poem.stanzas)
tr_lines = " | ".join(" | ".join(s.translated_lines) for s in poem.stanzas)
ultra = f"""LANGUAGE: Assamese | STANZAS: 1
SOURCE: {src_lines}
TRANSLATION: {tr_lines}
Return ONE minified JSON with keys: recitation_style (one of: lament/devotional/celebratory/reflective/declarative), emotional_arc (string), stanzas (array with index/emotion/tone/translation_quality/loss_note/metaphor_spans), cultural_entities (array with term/romanization/category/stanza_index/preserved/translation_note).
Emotion options: grief/longing/devotion/peace/celebration/resilience/anger/fear
Tone options: lament/whisper/declaration/prayer/wonder/defiance/tenderness
Quality options: faithful/partial/lost"""
print(f"Ultra prompt: {len(ultra)} chars")
msgs_ultra = [{"role": "user", "content": ultra}]
for budget in [512, 768, 1024, 1536, 2048]:
    call_and_show("gemini/ultra", "gemini", msgs_ultra, budget)

# ── TEST 4: Completion test — can proxy return 400+ chars? ────────────────────
print()
print("=== TEST 4: Long JSON completion test ===")
long_json_prompt = (
    "Return ONLY this exact JSON (no markdown), filling placeholders with real Assamese poem annotation values:\n"
    '{"recitation_style":"FILL_STYLE","emotional_arc":"FILL_ARC","stanzas":[{"index":1,"emotion":"FILL_EMO",'
    '"tone":"FILL_TONE","translation_quality":"FILL_QUAL","loss_note":"FILL_LOSS_NOTE_IF_NOT_FAITHFUL_ELSE_EMPTY","metaphor_spans":[]}],'
    '"cultural_entities":[{"term":"FILL_ASSAMESE_TERM_FROM_SOURCE","romanization":"FILL_ROMAN","category":"FILL_CAT",'
    '"stanza_index":1,"preserved":false,"translation_note":"FILL_WHY_LOST"}]}\n'
    f"SOURCE: {src_lines}\nTRANSLATION: {tr_lines}"
)
print(f"Long JSON prompt: {len(long_json_prompt)} chars")
for budget in [768, 1024, 1536, 2048]:
    call_and_show("gemini/longfill", "gemini", [{"role": "user", "content": long_json_prompt}], budget)
