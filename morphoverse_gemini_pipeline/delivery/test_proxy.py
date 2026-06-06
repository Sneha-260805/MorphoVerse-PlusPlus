"""Quick diagnostic: find the real max-output-token ceiling of the proxy."""
from api import LLMProxyClient

TOKEN = "7467da865bd89ad904e68bf1de7141a749e6d569d65c62a2"
c = LLMProxyClient(token=TOKEN)

# --- test 1: echo back a known long JSON ----------------------------------------
prompt = (
    "Return ONLY this minified JSON with NO changes, NO markdown, NO text before or after:\n"
    '{"recitation_style":"reflective","emotional_arc":"longing",'
    '"stanzas":[{"index":1,"emotion":"longing","tone":"tenderness",'
    '"translation_quality":"faithful","loss_note":"",'
    '"metaphor_spans":[{"source_term":"river","abstract_meaning":"flowing time"}]}],'
    '"cultural_entities":[{"term":"Ganga","romanization":"Ganga","category":"SACRED_RIVER",'
    '"stanza_index":1,"preserved":true,"translation_note":"preserved as Ganga"}]}'
)

for model in ("gemini", "gemini-3-flash"):
    for budget in (256, 512, 1024, 1500, 2048):
        try:
            r = c.chat(model, [{"role": "user", "content": prompt}], max_tokens=budget)
            txt = r["choices"][0]["message"]["content"]
            print(f"[{model}] max_tokens={budget}: got {len(txt)} chars -> {repr(txt[:80])}")
        except Exception as e:
            print(f"[{model}] max_tokens={budget}: ERROR {e}")
