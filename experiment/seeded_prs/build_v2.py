#!/usr/bin/env python3
"""Seeded PRs, version 2: the REAL pipeline PRs, each with ONE injected defect (S1-S5), plus two real PRs unchanged (C1, C2).

Why v2: in v1 the seeds were built from my own reference fixes while the reviewer variant that sees the author's artifacts
(spec/design/test report) was given the artifacts of the *real* pipeline runs, so those artifacts described different code than
the diff under review. v2 makes the author's artifacts describe the code that is reviewed.

Each seed is verified: the repo suite passes; the issue's hidden tests fail on defective seeds and pass on controls.
With --push the branch seeded2/<id> (one commit on the real PR's parent, message has [skip ci]) is pushed to the fork.
"""
import importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location("validate", REPO / "experiment/validation/validate.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
edit, HIDDEN = V.edit, V.HIDDEN


def m1(w):  # PR #15 (issue 1): the missing-path result is only applied to top-level paths
    edit(w / "tinydb/queries.py", "                return missing_result\n", "                return missing_result and len(self._path) == 1\n")

def m2(w):  # PR #14 (issue 2): the cache stores a shallow copy again, so the miss-path result shares objects with the cache
    edit(w / "tinydb/table.py", "            self._query_cache[cond] = copy.deepcopy(docs)", "            self._query_cache[cond] = docs[:]")

def m3(w):  # PR #10 (issue 3): count() without a condition skips empty documents ({}), so it disagrees with len(table)
    edit(w / "tinydb/table.py", "            return len(self)\n", "            return len([doc for doc in self if doc])\n")

def m4(w):  # PR #17 (issue 4): documents without the field are silently skipped instead of raising KeyError
    edit(w / "tinydb/operations.py", "        value = doc[field]\n", "        if field not in doc:\n            return\n        value = doc[field]\n")

def m5(w):  # PR #26 (issue 5): sorted by the raw (string) key, so '10' sorts before '2'
    edit(w / "tinydb/table.py", "key=lambda item: self.document_id_class(item[0])", "key=lambda item: item[0]", 2)

nothing = lambda w: None
SEEDS = {
    "S1": dict(issue=1, pr_branch="autose/issue-1", ctx="issue1", fn=m1, defect="nested-path-missing", expected="changes",
               desc="PR #15 with `return missing_result` changed to `missing_result and len(self._path) == 1`: `!=` is fixed for top-level fields only.",
               how="try a nested path; compare `q != v` with `~(q == v)`"),
    "S2": dict(issue=2, pr_branch="autose/issue-2", ctx="issue2", fn=m2, defect="cache-shares-objects-on-miss", expected="changes",
               desc="PR #14 with the cache storing `docs[:]` instead of a deep copy: the first (miss) result shares objects with the cache. (The real PR also rewrote the contract test; that is part of every version of this PR.)",
               how="mutate the result of the FIRST search, then search again"),
    "S3": dict(issue=3, pr_branch="autose/issue-3", ctx="issue3", fn=m3, defect="skips-empty-documents", expected="changes",
               desc="PR #10 with `len(self)` replaced by a count that skips empty documents, so `count()` disagrees with `len(table)`.", how="insert an empty document {} and compare `count()` with `len(db)`"),
    "S4": dict(issue=4, pr_branch="autose/issue-4", ctx="issue4", fn=m4, defect="silently-skips-missing-field", expected="changes",
               desc="PR #17 with an early return when the field is missing (sibling operations raise KeyError).", how="update a document that lacks the field"),
    "S5": dict(issue=5, pr_branch="autose/issue-5", ctx="issue5-ask", fn=m5, defect="lexical-order", expected="changes",
               desc="PR #26 with the sort key changed to the raw string id: id 10 sorts before id 2.", how="insert 12 documents and read them back"),
    "C1": dict(issue=3, pr_branch="autose/issue-3", ctx="issue3", fn=nothing, defect=None, expected="approve", desc="PR #10 unchanged (control).", how="n/a"),
    "C2": dict(issue=4, pr_branch="autose/issue-4", ctx="issue4", fn=nothing, defect=None, expected="approve", desc="PR #17 unchanged (control).", how="n/a"),
}



def remove_tests(w, names):
    """Delete the top-level test functions that expose the injected defect, as if the author had not written them."""
    import ast
    removed = []
    for f in (w / "tests").rglob("test_*.py"):
        src = f.read_text(); tree = ast.parse(src); lines = src.splitlines(keepends=True); cut = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
                cut.append((start, node.end_lineno)); removed.append(f"{f.name}::{node.name}")
        for a, b in sorted(cut, reverse=True):
            del lines[a:b]
        if cut:
            f.write_text("".join(lines))
    return removed


def mechanical_test_report(w, diff, suite):
    """Same facts the orchestrator's own test_report.md contains: suite result and the tests the diff adds."""
    import re
    added = re.findall(r"^\+def (test_\w+)", diff, re.M)
    return ("# Test report\n\n- full suite passed: **True**\n- result: " + suite + "\n- tests added or changed by this change:\n"
            + "".join(f"  - {t}\n" for t in added))


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main(push):
    tmp = Path(tempfile.mkdtemp(prefix="seeds2-")); ok = True
    (HERE / "v2").mkdir(exist_ok=True)
    try:
        for sid, s in SEEDS.items():
            head = f"origin/{s['pr_branch']}"
            parent = run(["git", "rev-parse", f"{head}~1"], REPO).stdout.strip()
            real_diff = run(["git", "diff", f"{head}~1", head], REPO).stdout
            w = tmp / sid
            run(["git", "worktree", "add", "-q", "--detach", str(w), parent], REPO)
            (tmp / f"{sid}.diff").write_text(real_diff)
            r = run(["git", "apply", str(tmp / f"{sid}.diff")], w)
            assert r.returncode == 0, r.stderr
            s["fn"](w)
            run(["git", "add", "-A"], w)
            diff = run(["git", "diff", "--cached"], w).stdout
            suite, sfail = V.pytest(w, w / "tests")
            dropped = []
            if s["defect"] and sfail:                       # the author's own tests would have caught it: assume the author did not write them
                dropped = remove_tests(w, set(sfail))
                run(["git", "add", "-A"], w)
                diff = run(["git", "diff", "--cached"], w).stdout
                suite, sfail = V.pytest(w, w / "tests")
            hidden, hf = V.pytest(w, HIDDEN / f"test_issue{s['issue']}_hidden.py")
            ctxdir = HERE / "context" / f"v2-{sid}"; ctxdir.mkdir(parents=True, exist_ok=True)
            for name in ("spec.md", "design.md"):
                shutil.copy(HERE / "context" / s["ctx"] / name, ctxdir / name)
            if dropped:                                      # defective seed: report describes THIS diff, not the real PR's
                (ctxdir / "test_report.md").write_text(mechanical_test_report(w, diff, suite))
            else:
                shutil.copy(HERE / "context" / s["ctx"] / "test_report.md", ctxdir / "test_report.md")
            hp = " failed" not in hidden
            good = ("failed" not in suite) and (hp if s["defect"] is None else not hp)
            ok &= good
            print(f"{sid} issue {s['issue']} {str(s['defect']):30s} suite: {suite:24s} hidden: {hidden:26s} {'OK' if good else 'UNEXPECTED'}")
            (HERE / "v2" / f"{sid}.patch").write_text(diff)
            (HERE / "v2" / f"{sid}.json").write_text(json.dumps({
                "id": sid, "set": "v2", "issue": s["issue"], "defect": s["defect"], "expected_verdict": s["expected"], "description": s["desc"],
                "how_to_find": s["how"], "branch": f"seeded2/{sid.lower()}", "base": "parent", "context": f"v2-{sid}", "derived_from": s["pr_branch"],
                "suite": suite, "hidden_tests": hidden, "hidden_failed": hf, "tests_removed_because_they_expose_the_defect": dropped}, indent=1))
            if push and good:
                run(["git", "checkout", "-q", "-b", f"seeded2/{sid.lower()}"], w)
                run(["git", "-c", "user.name=seed-builder", "-c", "user.email=seed@users.noreply.github.com", "commit", "-q", "-m", f"seeded2 {sid}: {s['defect'] or 'real PR unchanged'} [skip ci]"], w)
                r = run(["git", "push", "-q", "--force", "origin", f"seeded2/{sid.lower()}"], w)
                print("   pushed" if r.returncode == 0 else "   push failed: " + r.stderr[-200:])
            run(["git", "worktree", "remove", "--force", str(w)], REPO)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main("--push" in sys.argv)
