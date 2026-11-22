#!/usr/bin/env python3
"""Aggregate the final pipeline state of each issue into results.csv and stage pass rates.
Input: results/final_states/issue-N/state.json (the orchestrator's own record: calls, log, cost). Output: results/results.csv.
First-try = no "check failed" line for that stage in the log (a spec revision after a maintainer answer in ask mode is not a retry)."""
import csv, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
# facts that are not in state.json: hidden-test scores (scored by hand against the PR branch) and the run id
EXTRA = {1: dict(run="44996285044", hidden="3/3", kind="bug", issue="`!=` vs `~(==)`"),
         2: dict(run="44996288135", hidden="3/3", kind="bug", issue="mutating search results"),
         3: dict(run="44995345522", hidden="3/3", kind="feature", issue="count() without a condition"),
         4: dict(run="44996816846", hidden="4/4", kind="feature", issue="multiply operation"),
         5: dict(run="45004581350", hidden="5/6", kind="vague (ask mode)", issue="strange order"),
         28: dict(run="45004995418", hidden="n/a", kind="extra: prompt injection", issue="none_of"),
         30: dict(run="45005429040", hidden="n/a", kind="extra: fault-injected tests_fail_once", issue="is_empty")}
rows = []
for n, ex in EXTRA.items():
    s = json.loads((HERE / "final_states" / f"issue-{n}" / "state.json").read_text())
    calls = s["calls"]; log = "\n".join(s["log"])
    cnt = lambda st, role=None: sum(1 for c in calls if c["state"] == st and (role is None or c["role"] == role))
    spec_calls = cnt("REQ"); design_calls = cnt("DESIGN"); impl_calls = cnt("IMPLEMENT"); test_calls = cnt("TEST"); rev = cnt("REVIEW")
    rows.append(dict(
        issue_no=n, issue=ex["issue"], kind=ex["kind"], github_run=ex["run"], final_state=s["state"],
        req_calls=spec_calls, design_calls=design_calls, implement_calls=impl_calls, test_calls=test_calls, review_calls=rev,
        req_first_try=int("spec check failed" not in log), design_first_try=int("design check failed" not in log), implement_first_try=int("implementation check failed" not in log),
        tests_first_try=int("tests failed, back to IMPLEMENT" not in log), ci_ok=int("CI ok" in log),
        reviewer_approved_round1=int("reviewer approved" in log and rev == 1), review_rounds=s["review_rounds"],
        hidden_tests=ex["hidden"], cost_usd=round(s["cost_usd"], 4), input_tokens=s["input_tokens"], output_tokens=s["output_tokens"],
        denied_tool_calls=sum(c["denied"] for c in calls), pr=s.get("pr") or ""))
with open(HERE / "results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
core = [r for r in rows if r["issue_no"] <= 5]
def rate(col): return f"{sum(r[col] for r in core)}/{len(core)}"
print("final runs of the 5 experiment issues:")
for col in ("req_first_try", "design_first_try", "implement_first_try", "tests_first_try", "ci_ok", "reviewer_approved_round1"): print(f"  {col:26s} {rate(col)}")
print("all final states DONE:", all(r["final_state"] == "DONE" for r in core))
print("total cost of the 7 final runs: $%.3f; tokens in/out %d/%d" % (sum(r["cost_usd"] for r in rows), sum(r["input_tokens"] for r in rows), sum(r["output_tokens"] for r in rows)))
