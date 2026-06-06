import sys, os, asyncio, json
os.environ['LLM_PROXY_TOKEN'] = '7467da865bd89ad904e68bf1de7141a749e6d569d65c62a2'

from pathlib import Path
from poem_annotator.dataset import preprocess_poem

def load_dataset_file(path):
    import json
    with Path(path).open('r', encoding='utf-8') as f:
        return json.load(f)
from poem_annotator.models import fetch_gemini_annotation
from poem_annotator.main import build_prompt_bundle
from poem_annotator.config import DEFAULT_BASE_URL

token = os.environ['LLM_PROXY_TOKEN']

for pid, lang in [('MV++_1443', 'telugu'), ('MV++_1559', 'urdu'), ('MV++_1569', 'urdu')]:
    print(f'--- {pid} ---')
    raw = load_dataset_file(f'morphoverse_jsons/{lang}_poems.json')
    poems_list = raw if isinstance(raw, list) else raw.get('poems', raw)
    rec = next(r for r in poems_list if isinstance(r, dict) and r.get('poem_id') == pid)
    poem = preprocess_poem(rec)
    sys_p, usr_p, rep_p = build_prompt_bundle(poem, {})
    print(f'stanzas={len(poem.stanzas)}, prompt_chars={len(sys_p)+len(usr_p)}, budget=2048')
    result = asyncio.run(fetch_gemini_annotation(poem, sys_p, usr_p, rep_p, token, DEFAULT_BASE_URL))
    status = result['status']
    reason = (result['discard_reason'] or '')[:120]
    raw = (result.get('raw_text') or '')[:150]
    print(f'status={status}')
    print(f'reason={reason}')
    print(f'raw_start={repr(raw)}')
    print()
