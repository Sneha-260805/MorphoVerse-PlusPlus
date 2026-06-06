import json
from pathlib import Path
from collections import defaultdict

stats = defaultdict(lambda: {"done": 0, "fail": 0, "entities": 0})
failed_ids = []

for f in sorted(Path("output_test").rglob("*.json")):
    lang = f.parent.name
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    status = d.get("status", "")
    entities = len(d.get("annotation", {}).get("cultural_entities", []))
    if status in ("completed", "salvaged"):
        stats[lang]["done"] += 1
        stats[lang]["entities"] += entities
    else:
        stats[lang]["fail"] += 1
        failed_ids.append(d.get("poem_id", str(f.stem)))

total_done = sum(v["done"] for v in stats.values())
total_fail = sum(v["fail"] for v in stats.values())
total_ent  = sum(v["entities"] for v in stats.values())

print("TOTAL: done=%d  failed=%d  entities=%d" % (total_done, total_fail, total_ent))
print("%-14s %4s %4s %5s %8s" % ("Language", "Done", "Fail", "Total", "Entities"))
print("-" * 42)
for lang in sorted(stats):
    v = stats[lang]
    print("%-14s %4d %4d %5d %8d" % (lang, v["done"], v["fail"], v["done"] + v["fail"], v["entities"]))

print()
for pid in failed_ids:
    print("  FAILED:", pid)
