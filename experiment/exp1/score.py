#!/usr/bin/env python3
"""Score Experiment 1 locally (the hidden tests are private and not available in Actions).

Usage: python experiment/exp1/score.py <dir with the downloaded exp1 artifacts> [more dirs...] [--out results/exp1]
For every run directory `<mode>_issue<N>_rep<R>` (state.json, spec.md, design.md, diff.patch, test_report.md): apply diff.patch to a clean
worktree of the run's base commit, run the issue's hidden tests and the repo suite, and write one CSV row. Prints a summary per mode.
"""
import csv, json, re, subprocess, sys, tempfile, shutil
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
HIDDEN = Path.home() / "a3_private" / "hidden_tests"
PY = sys.executable
args = [x for x in sys.argv[1:] if not x.startswith("--")]
def opt(name, default):
    if name in sys.argv:
        v = sys.argv[sys.argv.index(name) + 1]; args.remove(v); return Path(v)
    return default
out = opt("--out", ROOT / "results/exp1")
GITREPO = opt("--repo", ROOT)          # repository that contains the runs' base commits


def run(cmd, cwd): return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def pytest(w, target):
    r = run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov", "-c", "/dev/null", str(target)], w)
    passed = int((re.search(r"(\d+) passed", r.stdout) or [0, 0])[1]); failed = int((re.search(r"(\d+) failed", r.stdout) or [0, 0])[1])
    return passed, failed, re.findall(r"FAILED \S*::(\w+)", r.stdout)

rows = []
tmp = Path(tempfile.mkdtemp(prefix="exp1-score-"))
for root in args:
    for d in sorted(Path(root).rglob("state.json")):
        run_dir = d.parent; m = re.match(r"(\w+)_issue(\d+)_rep(\d+)", run_dir.name)
        if not m: continue
        mode, n, rep = m.group(1), int(m.group(2)), int(m.group(3))
        st = json.loads(d.read_text()); log = "\n".join(st["log"])
        w = tmp / run_dir.name
        r = run(["git", "worktree", "add", "-q", "--detach", str(w), st["base_sha"] or "HEAD"], GITREPO)
        if r.returncode:
            raise SystemExit(f"cannot check out base commit {st['base_sha']} of {run_dir.name} in {GITREPO}: {r.stderr.strip()}")
        patch = (run_dir / "diff.patch").resolve(); applied = False      # absolute: git apply runs inside the worktree
        if patch.exists() and patch.read_text().strip():
            ap = run(["git", "apply", str(patch)], w); applied = ap.returncode == 0
            if not applied:
                raise SystemExit(f"cannot apply {patch} onto {st['base_sha']}: {ap.stderr.strip()[:300]}")
        hp, hf, hnames = pytest(w, HIDDEN / f"test_issue{n}_hidden.py") if applied else (0, 0, [])
        sp, sf, _ = pytest(w, w / "tests") if applied else (0, 0, [])
        extra_failed = sum(1 for x in hnames if x.startswith("test_extra"))
        rows.append(dict(mode=mode, issue=n, rep=rep, final_state=st["state"], completed=int(st["state"] == "DONE"), diff_applied=int(applied),
                         hidden_passed=hp, hidden_failed=hf, hidden_failed_excluding_extra=hf - extra_failed, suite_failed=sf,
                         all_hidden_pass=int(applied and hf == 0), all_hidden_pass_excluding_extra=int(applied and hf - extra_failed == 0),
                         spec_retries=log.count("spec check failed"), design_retries=log.count("design check failed"),
                         implement_retries=log.count("implementation check failed"), test_retries=st.get("test_retries", 0),
                         agent_calls=len(st["calls"]), turns=sum(c["turns"] for c in st["calls"]), denied=sum(c["denied"] for c in st["calls"]),
                         cost_usd=round(st["cost_usd"], 4), input_tokens=st["input_tokens"], output_tokens=st["output_tokens"]))
        run(["git", "worktree", "remove", "--force", str(w)], GITREPO)
shutil.rmtree(tmp, ignore_errors=True)
out.mkdir(parents=True, exist_ok=True)
if rows:
    with open(out / "results.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
by = defaultdict(list)
for r in rows: by[r["mode"]].append(r)
for mode, rs in sorted(by.items()):
    n = len(rs); avg = lambda k: sum(r[k] for r in rs) / n
    print(f"\n== {mode}: {n} runs | completed {sum(r['completed'] for r in rs)}/{n} | all hidden tests pass {sum(r['all_hidden_pass'] for r in rs)}/{n} "
          f"(excluding the 'extra' test {sum(r['all_hidden_pass_excluding_extra'] for r in rs)}/{n})")
    print(f"   retries per run: spec {avg('spec_retries'):.2f} design {avg('design_retries'):.2f} implement {avg('implement_retries'):.2f} tests {avg('test_retries'):.2f}")
    if all(r["diff_applied"] == 0 for r in rs): raise SystemExit("no diff was applied in any run: refusing to report scores")
    print(f"   per run: ${avg('cost_usd'):.4f}, {avg('agent_calls'):.1f} agent calls, {avg('turns'):.0f} turns, {avg('input_tokens')/1000:.0f}k in / {avg('output_tokens')/1000:.1f}k out tokens; total ${sum(r['cost_usd'] for r in rs):.3f}")
