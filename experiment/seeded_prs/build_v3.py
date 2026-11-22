#!/usr/bin/env python3
"""Seeds v3: NEW seeds for testing ADR-014 (reviewer compares with siblings; contract reversals are `approach` findings).

They were designed AFTER seeing the S4 miss and BEFORE the reviewer prompt was changed, and are NOT used to design the prompt.
  S6  sibling-convention defect: `!=` reuses the hash tag of `==`, so the query cache returns `==` results for `!=`.
  S7  unrequested contract reversal: a change that makes ids come back in ascending order (the issue-5 area) also makes
      remove(doc_ids=...) raise KeyError for missing ids (documented and tested as 'silently skipped'); the three tests that pin
      the contract are rewritten, the docstring is left stale.
  C3  correct control (the issue-1 fix, with tests).
Built on top of origin/master (which contains ARCHITECTURE.md). Each seed is verified before it is written.
"""
import importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location("validate", REPO / "experiment/validation/validate.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
edit, HIDDEN = V.edit, V.HIDDEN
PY = sys.executable


def s6(w):
    V.i1_A(w)
    edit(w / "tinydb/queries.py", "            ('!=', self._path, freeze(rhs)),\n            missing_result=True", "            ('==', self._path, freeze(rhs)),\n            missing_result=True")
    (w / "tests/test_seed_s6.py").write_text(
        "from tinydb import Query\n\n\ndef test_ne_matches_document_without_field():\n    assert (Query().nickname != 'bob')({'name': 'c'})\n"
        "    assert (Query().nickname != 'bob')({'nickname': 'al'})\n    assert not (Query().nickname != 'bob')({'nickname': 'bob'})\n\n\n"
        "def test_ne_is_negation_of_eq_for_top_level_fields():\n    doc = {'name': 'c'}\n    assert (Query().nickname != 'bob')(doc) == (~(Query().nickname == 'bob'))(doc)\n")

def s7(w):
    V.i5_A(w)       # ids come back in ascending order (the issue-5 area) ...
    S7_CODE(w)      # ... and, not asked for by any issue, remove(doc_ids=...) now raises for ids that do not exist
    tests = w / "tests/test_tinydb.py"
    edit(tests, "    assert db.remove(doc_ids=[99]) == []\n    assert len(db) == 3",
         "    with pytest.raises(KeyError):\n        db.remove(doc_ids=[99])\n    assert len(db) == 3")
    edit(tests, "    assert sorted(db.remove(doc_ids=[1, 99])) == [1]\n    assert len(db) == 2\n    assert db.get(doc_id=1) is None\n    assert db.get(doc_id=2) is not None",
         "    with pytest.raises(KeyError):\n        db.remove(doc_ids=[1, 99])\n    assert len(db) == 3\n    assert db.get(doc_id=1) is not None\n    assert db.get(doc_id=2) is not None")
    edit(tests, "    assert db.update({'int': 9}, doc_ids=[99]) == []\n    assert db.remove(doc_ids=[99]) == []",
         "    assert db.update({'int': 9}, doc_ids=[99]) == []\n    with pytest.raises(KeyError):\n        db.remove(doc_ids=[99])")
    (w / "tests/test_seed_s7.py").write_text(
        "from tinydb import TinyDB\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_update_returns_ids_ascending():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])\n    assert db.update({'a': 9}, doc_ids=[3, 1, 2]) == [1, 2, 3]\n")


def S7_CODE(w):
    edit(w / "tinydb/table.py", "            def updater(table: dict):\n                # Filter to IDs that exist *before* performing any removals,",
         "            def updater(table: dict):\n                missing = [doc_id for doc_id in requested_ids if doc_id not in table]\n                if missing:\n                    raise KeyError(missing[0])\n                # Filter to IDs that exist *before* performing any removals,")


def c3(w):
    V.i1_A(w)
    (w / "tests/test_seed_c3.py").write_text(
        "from tinydb import Query, TinyDB\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_ne_matches_document_without_field():\n    assert (Query().nickname != 'bob')({'name': 'c'})\n"
        "    assert not (Query().nickname != 'bob')({'nickname': 'bob'})\n\n\ndef test_ne_and_eq_do_not_share_cached_results():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert_multiple([{'n': 1}, {'n': 2}])\n    assert len(db.search(Query().n == 1)) == 1\n    assert len(db.search(Query().n != 1)) == 1\n")

# demonstrations that the defect is real (run inside the seed's worktree); they print DEFECT or OK
DEMO_S6 = ("from tinydb import TinyDB, where\nfrom tinydb.storages import MemoryStorage\ndb = TinyDB(storage=MemoryStorage)\ndb.insert_multiple([{'a': 1}, {'a': 2}])\n"
           "eq = db.search(where('a') == 1); ne = db.search(where('a') != 1)\nprint('DEFECT' if ne == eq else 'OK', 'ne returned', ne)\n")
DEMO_S7 = ("from tinydb import TinyDB\nfrom tinydb.storages import MemoryStorage\ndb = TinyDB(storage=MemoryStorage)\ndb.insert({'a': 1})\n"
           "try:\n    r = db.remove(doc_ids=[99]); print('OK documented behaviour kept, returned', r)\n"
           "except KeyError as e:\n    print('DEFECT remove(doc_ids=[99]) now raises KeyError', e)\n")
DEMO_NONE = "print('OK')\n"

SEEDS = {
    "S6": dict(fn=s6, issue=1, defect="hash-tag-collision-with-sibling", expected="changes", issue_type="code", demo=DEMO_S6,
               desc="`!=` is fixed for missing fields, but its hash tuple uses the tag of `==`, so `where('a') != 1` and `where('a') == 1` share a cache entry and the second search returns the first's result. Violates the per-operator hash convention of every sibling operator (and ARCHITECTURE.md constraint 5).",
               how="compare `__ne__` with `__eq__`/`__lt__` (each has its own hash tag), or run `==` then `!=` on the same table"),
    "S7": dict(fn=s7, issue=5, defect="unrequested-contract-reversal-with-rewritten-tests", expected="changes", issue_type="approach", demo=DEMO_S7,
               desc="A change that makes ids come back in ascending order (the issue-5 area) also makes `remove(doc_ids=...)` raise KeyError for missing ids. The documented and tested rule is 'silently skipped' (see #591, mirrors `get(doc_ids=...)`); the three tests that pin it (`test_remove_ids_missing`, `test_remove_ids_mixed`, `test_doc_id_missing_consistency`) are rewritten and the docstring is left stale. No issue asks for this.",
               how="read the diff of existing tests and compare with the `remove` docstring and `get(doc_ids=...)`"),
    "C3": dict(fn=c3, issue=1, defect=None, expected="approve", issue_type="none", demo=DEMO_NONE,
               desc="Correct control: the issue-1 fix with its own tests, including a test that `==` and `!=` do not share cached results.", how="n/a"),
}


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main(push):
    (HERE / "v3").mkdir(exist_ok=True)
    base = run(["git", "rev-parse", "origin/master"], REPO).stdout.strip()
    tmp = Path(tempfile.mkdtemp(prefix="seeds3-")); ok = True
    try:
        for sid, s in SEEDS.items():
            w = tmp / sid
            run(["git", "worktree", "add", "-q", "--detach", str(w), base], REPO)
            s["fn"](w)
            run(["git", "add", "-A"], w)
            diff = run(["git", "diff", "--cached"], w).stdout
            suite, sfail = V.pytest(w, w / "tests")
            hidden, hf = V.pytest(w, HIDDEN / f"test_issue{s['issue']}_hidden.py")
            demo = run([PY, "-c", s["demo"]], w).stdout.strip()
            # for S7 also prove it IS a contract reversal: the two pinned tests fail on the unmodified (pre-rewrite) tests
            pinned = ""
            if sid == "S7":
                p = tmp / "S7pre"; run(["git", "worktree", "add", "-q", "--detach", str(p), base], REPO)
                V.i5_A(p)
                S7_CODE(p)
                _, pinned = V.pytest(p, p / "tests"); run(["git", "worktree", "remove", "--force", str(p)], REPO)
            defective = s["defect"] is not None
            good = ("failed" not in suite) and (("DEFECT" in demo) if defective else ("OK" in demo)) and (not defective or sid != "S7" or len(set(pinned)) >= 3)
            ok &= good
            print(f"{sid} issue {s['issue']} {str(s['defect']):52s} suite: {suite:24s} hidden: {hidden:22s} demo: {demo[:60]:60s} {'OK' if good else 'UNEXPECTED'}" + (f"\n    existing tests that fail before the rewrite: {sorted(set(pinned))}" if pinned else ""))
            (HERE / "v3" / f"{sid}.patch").write_text(diff)
            (HERE / "v3" / f"{sid}.json").write_text(json.dumps({
                "id": sid, "set": "v3", "issue": s["issue"], "defect": s["defect"], "expected_verdict": s["expected"], "expected_issue_type": s["issue_type"],
                "description": s["desc"], "how_to_find": s["how"], "branch": f"seeded3/{sid.lower()}", "base": "parent", "built_on": base,
                "suite": suite, "hidden_tests_of_the_issue": hidden, "defect_demonstration": demo,
                "existing_tests_that_fail_before_rewrite": sorted(set(pinned))}, indent=1))
            if push and good:
                run(["git", "-c", "user.name=seed-builder", "-c", "user.email=seed@users.noreply.github.com", "commit", "-q", "-m", f"seeded3 {sid}: {s['defect'] or 'correct control'} [skip ci]"], w)
                r = run(["git", "push", "-q", "--force", "origin", f"HEAD:refs/heads/seeded3/{sid.lower()}"], w)
                print("   pushed" if r.returncode == 0 else "   PUSH FAILED: " + r.stderr[-400:]); ok &= r.returncode == 0
            run(["git", "worktree", "remove", "--force", str(w)], REPO)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main("--push" in sys.argv)
