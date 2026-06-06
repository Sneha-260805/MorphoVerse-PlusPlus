import sys
sys.stdout.reconfigure(encoding='utf-8')

from poem_annotator.models import term_in_source, _strip_ascii_gloss

cases = [
    ("చల్లగా వీచే గాలి (cold wind)", "చల్లగా వీచే గాలి, ఒక్కసారిగా నన్ను తాకి చెప్పింది"),
    ("మెరుపు నువ్వే (you are the lightning)", "కను రెప్పలకే మాటలు వస్తే , ఛెబుతాయేమో నా కళ్ళను కమ్మిన మెరుపు నువ్వే అని"),
    ("మధుర క్షణం (sweetest moment)", "తిరిగి చూసిన ఆ క్షణం, ఏ జీవితానికి అదే మధుర క్షణం"),
    ("కను రెప్పలకే మాటలు వస్తే (if eyelids could speak)", "కను రెప్పలకే మాటలు వస్తే , ఛెబుతాయేమో నా కళ్ళను కమ్మిన మెరుపు నువ్వే అని"),
    ("నా దారి వైపు గా చూడు (look my way)", "నేనెందుకు వచ్చానో తెలుసా, ఐతే నా దారి వైపు గా చూడు యని"),
]

for term, source in cases:
    stripped = _strip_ascii_gloss(term)
    result = term_in_source(term, source)
    print(f"term: {term!r}")
    print(f"stripped: {stripped!r}")
    print(f"in_source: {result}")
    print()
