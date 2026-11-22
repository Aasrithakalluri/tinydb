#!/usr/bin/env python3
"""Score reviewer results: python experiment/seeded_prs/score.py results/seeded_review/results_A.jsonl [results_B.jsonl ...]
catch rate = changes on a defective seed; false approval = approve on a defective seed; false rejection = changes on a control.
Reports the raw verdict (what the model said) and the final verdict (after the pipeline overrules approvals with no test run)."""
import json, sys
from collections import defaultdict

for path in sys.argv[1:]:
    rows = [json.loads(l) for l in open(path) if l.strip()]
    if not rows: continue
    print(f"\n== {path}  (variant {rows[0]['variant']}, {len(rows)} reviews, ${sum(r['cost_usd'] for r in rows):.3f}, "
          f"{sum(r['in_tokens'] for r in rows)} in / {sum(r['out_tokens'] for r in rows)} out tokens)")
    for kind in ("raw_verdict", "final_verdict"):
        d = [r for r in rows if r["defect"]]; c = [r for r in rows if not r["defect"]]
        caught = sum(1 for r in d if r[kind] == "changes"); fr = sum(1 for r in c if r[kind] == "changes")
        print(f"  {kind:14s} caught {caught}/{len(d)} defective reviews | false approvals {len(d)-caught}/{len(d)} | false rejections {fr}/{len(c)}")
    per = defaultdict(list)
    for r in rows: per[r["seed"]].append(r)
    for sid in sorted(per):
        v = [r["final_verdict"] or "none" for r in per[sid]]
        print(f"  {sid} (expected {per[sid][0]['expected']}): {', '.join(v)} | tests run {sum(r['tests_run'] for r in per[sid])}/{len(v)}")
