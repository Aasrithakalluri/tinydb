#!/usr/bin/env python3
"""Experiment 1 (ADR-001): one agent for stages 1-4 ("single") vs the three-agent pipeline ("multi"), stages 1-4 only.

Each (issue, repeat, mode) is a fresh run: state is reset, the checkout is reset to the baseline commit, nothing is posted anywhere and
no PR/CI/reviewer is used (the run stops after stage 4). Hidden tests are NOT available in Actions; this script saves each run's artifacts
(state.json, spec.md, design.md, diff.patch, test_report.md) and `experiment/exp1/score.py` scores them locally.
Order is repeat-major so that a budget stop leaves complete, balanced repeats.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, importlib
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--issues", default="1,2,3,4,5")
ap.add_argument("--modes", default="multi,single")
ap.add_argument("--repeats", type=int, default=2)
ap.add_argument("--budget", type=float, default=0.60, help="stop starting new runs once this many USD have been spent")
ap.add_argument("--per-run", type=float, default=0.20, help="cap for one run")
ap.add_argument("--out", default="exp1-out")
a = ap.parse_args()

ROOT = Path(__file__).resolve().parent.parent
os.environ.update(AUTOSE_STOP_AFTER="TEST", AUTOSE_QUIET="1", AUTOSE_ISSUES_DIR=str(ROOT / "experiment/issues"),
                  AUTOSE_RUN_BUDGET_USD=str(a.per_run), GITHUB_REPOSITORY=os.environ.get("GITHUB_REPOSITORY", "Aasrithakalluri/tinydb"))
sys.path.insert(0, str(ROOT / "workflow"))
BASE = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
assert not str(out).startswith(str(ROOT) + os.sep), f"--out must be OUTSIDE the repository ({ROOT}): `git add -A` stages it and `git clean` deletes it between runs"
# The orchestrator does `git add -A`, so a run's working files must NEVER live inside the repository checkout (a first attempt did, and
# every run failed the scope check on its own artifacts). Runs write to a temp dir outside the repo; finished runs are copied to --out.
WORK = Path(tempfile.mkdtemp(prefix="exp1-work-"))
assert not str(WORK).startswith(str(ROOT)), "work dir must be outside the repository"
spent = 0.0
for rep in range(1, a.repeats + 1):
    for n in [int(x) for x in a.issues.split(",")]:
        for mode in a.modes.split(","):
            if spent >= a.budget:
                print(f"budget ${a.budget} reached; stopping"); sys.exit(0)
            os.environ["AUTOSE_MODE"] = mode
            subprocess.run(["git", "reset", "-q", "--hard", BASE], cwd=ROOT); subprocess.run(["git", "clean", "-fdq"], cwd=ROOT)
            import orchestrator                      # re-import so module-level settings see this run's env
            importlib.reload(orchestrator)
            name = f"{mode}_issue{n}_rep{rep}"
            art = WORK / name
            shutil.rmtree(art, ignore_errors=True)
            try:
                run = orchestrator.Run(n, ROOT, art); run.run()
            except SystemExit:
                pass
            except Exception as e:
                print("ERROR", type(e).__name__, e)
            st = json.loads((art / "state.json").read_text()) if (art / "state.json").exists() else {}
            shutil.rmtree(out / name, ignore_errors=True)
            if art.exists():
                shutil.copytree(art, out / name)
            spent += st.get("cost_usd", 0.0)
            if "Credit balance is too low" in "\n".join(st.get("log", [])):
                print("The API reports 'Credit balance is too low'; stopping at once (no further runs, no results from this run)."); sys.exit(2)
            print(f"rep{rep} issue{n} {mode:6s} state={st.get('state')} cost=${st.get('cost_usd', 0):.3f} calls={len(st.get('calls', []))} total=${spent:.3f}", flush=True)
print(f"done; spent ${spent:.3f}")
