#!/usr/bin/env python3
"""Experiment 2 (ADR-008): run the reviewer on the seeded PRs (experiment/seeded_prs) and record its verdicts.

Variant A: Sonnet reviewer, fresh context, adversarial prompt (the production reviewer), sees issue + diff + checkout.
Variant B: Haiku reviewer, neutral prompt, ALSO sees the author's spec, design and test report (shared context).
Nothing is posted anywhere; results are written under --out as JSON lines plus the review text of every call.
"""
from __future__ import annotations

import argparse, json, os, re, subprocess, sys, tempfile, shutil, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import checks  # noqa: E402

BASE = "edff96aeb2616402e9489d46e90a592c05565621"
SEEDS = ["S1", "S2", "S3", "S4", "S5", "C1", "C2"]


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True).stdout


def issue_text(n: int) -> str:
    return "<untrusted_issue>\n" + (ROOT / "experiment/issues" / f"issue-{n}.md").read_text() + "\n</untrusted_issue>"


def raw_verdict(text: str) -> dict:
    m = re.findall(r"```json\s*(\{.*?\})\s*```", text or "", re.S)
    try:
        return json.loads(m[-1])
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["A", "B"], required=True)
    ap.add_argument("--set", dest="seedset", choices=["v1", "v2"], default="v2", help="v1 = seeds built from my reference fixes (pilot), v2 = real pipeline PRs with one injected defect")
    ap.add_argument("--seeds", default="all")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--out", default="seeded-review-out")
    ap.add_argument("--budget", type=float, default=1.5, help="stop when this many USD have been spent")
    ap.add_argument("--repo-url", default=os.environ.get("SEED_REPO_URL") or f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'Aasrithakalluri/tinydb')}.git")
    a = ap.parse_args()
    os.environ.pop("GITHUB_TOKEN", None); os.environ.pop("GH_TOKEN", None)       # agents never see a GitHub token
    from agents import run_agent
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    seeds = SEEDS if a.seeds == "all" else a.seeds.split(",")
    spent = 0.0
    results = out / f"results_{a.variant}.jsonl"
    for run in range(1, a.runs + 1):
        for sid in seeds:
            if spent >= a.budget:
                print(f"budget of ${a.budget} reached; stopping"); return
            label = json.loads((ROOT / "experiment/seeded_prs" / ("v2" if a.seedset == "v2" else ".") / f"{sid}.json").read_text())
            n = label["issue"]
            tmp = Path(tempfile.mkdtemp(prefix=f"seed-{sid}-"))
            clone = tmp / "repo"
            sh(["git", "clone", "-q", a.repo_url, str(clone)])
            sh(["git", "checkout", "-q", f"origin/{label['branch']}"], clone)
            base = "HEAD~1" if label.get("base") == "parent" else BASE
            diff = sh(["git", "diff", f"{base}..HEAD"], clone)
            patch = ROOT / "experiment/seeded_prs" / ("v2" if a.seedset == "v2" else ".") / f"{sid}.patch"
            if diff.strip() != patch.read_text().strip():          # a stale or wrong branch would silently invalidate the experiment
                raise SystemExit(f"seed {sid}: branch {label['branch']} does not match {patch.name}; re-run build and push before reviewing")
            if a.variant == "A":
                role, files = "reviewer", ["prompts/common.md", "prompts/reviewer.md"]
                prompt = (f"Review the pull request for this issue.\n\n{issue_text(n)}\n\n## Diff of the pull request\n```diff\n{diff[:30000]}\n```\n\n"
                          "Your working directory is a clean checkout at the pull request's latest commit.")
            else:
                ctx = ROOT / "experiment/seeded_prs/context" / label.get("context", f"issue{n}")
                role, files = "reviewer_b", ["prompts/common.md", "prompts/reviewer_shared.md"]
                prompt = (f"Review this pull request.\n\n{issue_text(n)}\n\n## Author's spec (spec.md)\n{(ctx / 'spec.md').read_text()[:9000]}\n\n"
                          f"## Author's design (design.md)\n{(ctx / 'design.md').read_text()[:5000]}\n\n## Author's test report (test_report.md)\n{(ctx / 'test_report.md').read_text()[:3000]}\n\n"
                          f"## Diff of the pull request\n```diff\n{diff[:30000]}\n```")
            system = "\n\n".join((HERE / f).read_text() for f in files)
            t0 = time.time()
            res = run_agent(role, system, prompt, clone, budget_usd=min(0.4, a.budget - spent))
            shutil.rmtree(tmp, ignore_errors=True)
            raw = raw_verdict(res.text)
            final, ran = checks.parse_verdict(res.text, res.tool_log)
            spent += res.cost_usd
            row = {"variant": a.variant, "set": a.seedset, "run": run, "seed": sid, "issue": n, "expected": label["expected_verdict"], "defect": label["defect"],
                   "raw_verdict": raw.get("verdict"), "final_verdict": final.get("verdict"), "issue_type": final.get("issue_type"),
                   "tests_run": ran, "findings": len(raw.get("findings", [])), "turns": res.turns, "cost_usd": round(res.cost_usd, 4),
                   "in_tokens": res.input_tokens, "out_tokens": res.output_tokens, "stop": res.stop_reason, "seconds": round(time.time() - t0)}
            with results.open("a") as f:
                f.write(json.dumps(row) + "\n")
            (out / f"review_{a.variant}_{sid}_run{run}.md").write_text(res.text or "")
            print(f"{a.variant} run{run} {sid}: raw={row['raw_verdict']} final={row['final_verdict']} expected={row['expected']} tests_run={ran} ${row['cost_usd']}", flush=True)
    print(f"total spent: ${spent:.3f}")


if __name__ == "__main__":
    main()
