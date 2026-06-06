import sys, os, io
os.environ["PYTHONIOENCODING"] = "utf-8"
out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
from api import LLMProxyClient, LLMProxyError

TOKEN = "7467da865bd89ad904e68bf1de7141a749e6d569d65c62a2"
BASE_URL = "https://llmproxy.magnocode.tech"
c = LLMProxyClient(token=TOKEN, base_url=BASE_URL)

simple_prompt = (
    'Annotate this Bengali poem about longing for homeland. '
    'Return ONLY minified JSON: {"rs":"STYLE","ea":"ARC","st":[{"i":1,"em":"EMOTION","to":"TONE","tq":"QUALITY","ln":"","ms":[]}],"ce":[]}\n'
    'SOURCE: তোমার বিনা আমার দিন কাটে | একা একা আলো ছাড়া\n'
    'TRANSLATION: Without you my days pass | Alone without light\n'
    'em options: grief/longing/devotion/peace/celebration  to options: lament/whisper/declaration/prayer/tenderness\n'
    'rs options: reflective/declarative/devotional/celebratory/lament  tq options: faithful/partial/lost'
)

for model in ["gemini", "gemini-3-flash", "claude"]:
    try:
        raw = c.chat(model, [{"role": "user", "content": simple_prompt}], max_tokens=512, temperature=0.1)
        ch = (raw.get("choices") or [{}])[0]
        content = ch.get("message", {}).get("content", "") or ""
        finish = ch.get("finish_reason", "?")
        out.write("[%s] len=%d finish=%s\n  -> %s\n" % (model, len(content), finish, repr(content[:250])))
    except Exception as e:
        out.write("[%s] ERROR: %s\n" % (model, str(e)[:120]))

out.flush()
