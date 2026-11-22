#!/usr/bin/env python3
"""Build the seeded reviewer-check PRs: real fixes with ONE deliberately injected defect each (S1-S5),
plus two correct controls (C1, C2). Each seed is verified before it is written:
  - the repository suite (including the seed's own tests) passes,
  - the issue's hidden tests FAIL on defective seeds and PASS on controls.
Outputs per seed: <ID>.patch (diff against the baseline) and <ID>.json (label). With --push, also pushes the
branch seeded/<id> (commit message contains [skip ci]) to the fork for the reviewer to check out.
"""
import importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location("validate", REPO / "experiment/validation/validate.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
edit, BASE, HIDDEN = V.edit, V.BASE, V.HIDDEN


def s1(w):   # issue 1: != now matches missing keys, but only for top-level paths (nested missing still excluded)
    q = w / "tinydb/queries.py"
    edit(q, "            allow_empty_path: bool = False\n    ) -> QueryInstance:", "            allow_empty_path: bool = False,\n            missing_result: bool = False\n    ) -> QueryInstance:")
    edit(q, "            except (KeyError, TypeError):\n                return False", "            except (KeyError, TypeError):\n                return missing_result and len(self._path) == 1")
    edit(q, "            ('!=', self._path, freeze(rhs))\n        )", "            ('!=', self._path, freeze(rhs)),\n            missing_result=True\n        )")
    (w / "tests/test_seed_s1.py").write_text(
        "from tinydb import Query, where\n\n\ndef test_ne_matches_document_without_field():\n"
        "    assert (Query().nickname != 'bob')({'name': 'c'})\n    assert (Query().nickname != 'bob')({'nickname': 'al'})\n"
        "    assert not (Query().nickname != 'bob')({'nickname': 'bob'})\n\n\ndef test_ne_is_negation_of_eq_top_level():\n"
        "    doc = {'name': 'c'}\n    assert (Query().nickname != 'bob')(doc) == (~(Query().nickname == 'bob'))(doc)\n")

def s2(w):   # issue 2: deep copy only on a cache HIT (the first, miss, result still shares objects with the cache) AND the existing contract test is rewritten
    t = w / "tinydb/table.py"
    edit(t, "from collections.abc import Callable", "import copy\nfrom collections.abc import Callable")
    edit(t, "            return cached_results[:]", "            return copy.deepcopy(cached_results)")
    # like the real PR #14: the existing test that pins the shared-documents contract is rewritten so the suite stays green
    edit(w / "tests/test_tinydb.py", "    # But a document inside it is the cached object, so mutating a\n    # top-level key or a nested value both reach the cache.\n    results2[0]['tags'].append('c')\n    results3 = db.search(query)\n    assert results3[0]['tags'] == ['a', 'b', 'c']",
         "    # Documents are copies, so mutating one does not reach the cache.\n    results2[0]['tags'].append('c')\n    results3 = db.search(query)\n    assert results3[0]['tags'] == ['a', 'b']")
    (w / "tests/test_seed_s2.py").write_text(
        "from tinydb import TinyDB, where\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_cached_search_returns_independent_copies():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert({'name': 'a', 'tags': ['x']})\n    q = where('name') == 'a'\n    db.search(q)\n"
        "    second = db.search(q)\n    second[0]['tags'].append('oops')\n    assert db.search(q)[0]['tags'] == ['x']\n")

def s3(w):   # issue 3: count() with no condition counts documents of ALL tables instead of this table
    t = w / "tinydb/table.py"
    edit(t, "    def count(self, cond: QueryLike) -> int:", "    def count(self, cond: Optional[QueryLike] = None) -> int:")
    edit(t, "        return len(self.search(cond))\n", "        if cond is None:\n            return sum(len(table) for table in (self._storage.read() or {}).values())\n        return len(self.search(cond))\n")
    (w / "tests/test_seed_s3.py").write_text(
        "from tinydb import TinyDB, where\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_count_without_condition():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    assert db.count() == 0\n    db.insert_multiple([{'a': 1}, {'a': 2}, {}])\n    assert db.count() == 3\n    assert db.count(where('a') == 1) == 1\n")

def s4(w):   # issue 4: multiply silently skips documents that lack the field (sibling operations raise KeyError)
    edit(w / "tinydb/operations.py", "def subtract(", "def multiply(field: str, n: Union[int, float]) -> Callable[[MutableMapping], None]:\n    \"\"\"\n    Multiply a given field in the document by ``n``.\n    \"\"\"\n    def transform(doc: MutableMapping):\n        if field in doc:\n            doc[field] *= n\n\n    return transform\n\n\ndef subtract(")
    (w / "tests/test_seed_s4.py").write_text(
        "from tinydb import TinyDB, where\nfrom tinydb.operations import multiply\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_multiply_scales_matching_documents():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 10, 'c': 'toys'}])\n    db.update(multiply('p', 3), where('c') == 'books')\n"
        "    assert db.get(where('c') == 'books')['p'] == 30\n    assert db.get(where('c') == 'toys')['p'] == 10\n\n\ndef test_multiply_float_factor():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert({'p': 10})\n    db.update(multiply('p', 1.5))\n    assert db.all()[0]['p'] == 15.0\n")

def s5(w):   # issue 5: sorted by the STRING key, so "10" sorts before "2" once a table has 10+ documents
    t = w / "tinydb/table.py"
    edit(t, "        for doc_id, doc in self._read_table().items():\n            # Convert documents to the document class", "        for doc_id, doc in sorted(self._read_table().items()):\n            # Convert documents to the document class")
    edit(t, "            for doc_id, doc in self._read_table().items()\n            if cond(doc)", "            for doc_id, doc in sorted(self._read_table().items())\n            if cond(doc)")
    (w / "tests/test_seed_s5.py").write_text(
        "from tinydb import TinyDB, where\nfrom tinydb.table import Document\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_results_are_ordered_by_document_id():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert({'n': 'a'})\n    db.insert(Document({'n': 'z'}, doc_id=5))\n    db.insert(Document({'n': 'c'}, doc_id=3))\n"
        "    assert [d.doc_id for d in db.all()] == [1, 3, 5]\n    assert [d.doc_id for d in db.search(where('n').exists())] == [1, 3, 5]\n")

def c1(w):   # control: correct fix for issue 3 (reference A) with tests
    V.i3_A(w)
    (w / "tests/test_seed_c1.py").write_text(
        "from tinydb import TinyDB, where\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_count_without_condition():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    assert db.count() == 0\n    db.insert_multiple([{'a': 1}, {'a': 2}, {}])\n    assert db.count() == 3\n\n\ndef test_count_is_per_table():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert({'a': 1})\n    other = db.table('other')\n    other.insert_multiple([{'a': 1}, {'a': 2}])\n    assert db.count() == 1 and other.count() == 2\n")

def c2(w):   # control: correct fix for issue 4 (reference A) with tests
    V.i4_A(w)
    (w / "tests/test_seed_c2.py").write_text(
        "import pytest\nfrom tinydb import TinyDB, where\nfrom tinydb.operations import multiply\nfrom tinydb.storages import MemoryStorage\n\n\ndef test_multiply_scales_matching_documents():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 10, 'c': 'toys'}])\n    db.update(multiply('p', 3), where('c') == 'books')\n"
        "    assert db.get(where('c') == 'books')['p'] == 30\n    assert db.get(where('c') == 'toys')['p'] == 10\n\n\ndef test_multiply_missing_field_raises_like_add():\n"
        "    db = TinyDB(storage=MemoryStorage)\n    db.insert({'x': 1})\n    with pytest.raises(KeyError):\n        db.update(multiply('p', 2))\n")

SEEDS = {
    "S1": dict(issue=1, fn=s1, defect="nested-path-missing", expected="changes", issue_type="code",
               desc="`!=` is fixed for top-level fields only; a missing nested path (`where('profile').city != 'x'`) still excludes the document, so `!=` is still not the negation of `==` there.",
               how_to_find="try a nested path, or compare `~(q == v)` with `q != v` on several shapes"),
    "S2": dict(issue=2, fn=s2, defect="copy-on-hit-only+rewritten-contract-test", expected="changes", issue_type="code",
               desc="Two defects. (1) Deep copy is made only when the cache is hit: the first (cache-miss) result still shares objects with the cache, so mutating it changes what the next search returns. (2) The existing test `test_query_cache_documents_are_shared_with_cache`, which pins a documented contract, is rewritten to expect the opposite so that the suite stays green; the docstring of `Table.search` that documents the contract is left stale.",
               how_to_find="mutate the result of the FIRST search, then search again; read the diff of existing tests and the Table.search docstring"),
    "S3": dict(issue=3, fn=s3, defect="counts-all-tables", expected="changes", issue_type="code",
               desc="`count()` without a condition sums the documents of every table in the database, not just this table.",
               how_to_find="insert into a second named table and compare `db.count()`"),
    "S4": dict(issue=4, fn=s4, defect="silently-skips-missing-field", expected="changes", issue_type="code",
               desc="`multiply` silently skips documents that lack the field, unlike `add`/`subtract`/`increment`, which raise KeyError. Hides data errors and breaks consistency with the sibling operations.",
               how_to_find="compare with `add` on a document without the field"),
    "S5": dict(issue=5, fn=s5, defect="lexical-order", expected="changes", issue_type="code",
               desc="Documents are sorted by the string key, so with 10 or more documents id 10 sorts before id 2.",
               how_to_find="insert 12 documents and read them back"),
    "C1": dict(issue=3, fn=c1, defect=None, expected="approve", issue_type="none",
               desc="Correct control (count() per table).", how_to_find="n/a"),
    "C2": dict(issue=4, fn=c2, defect=None, expected="approve", issue_type="none",
               desc="Correct control (multiply, raises KeyError on a missing field like add).", how_to_find="n/a"),
}


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main(push: bool):
    tmp = Path(tempfile.mkdtemp(prefix="seeds-"))
    ok = True
    try:
        for sid, s in SEEDS.items():
            w = tmp / sid
            run(["git", "worktree", "add", "-q", "--detach", str(w), BASE], REPO)
            s["fn"](w)
            run(["git", "add", "-A"], w)
            diff = run(["git", "diff", "--cached"], w).stdout
            suite, sfail = V.pytest(w, w / "tests")
            hidden, hfail = V.pytest(w, HIDDEN / f"test_issue{s['issue']}_hidden.py")
            hidden_pass = " failed" not in hidden
            good = ("failed" not in suite) and (hidden_pass if s["defect"] is None else not hidden_pass)
            ok &= good
            print(f"{sid} issue {s['issue']} defect={s['defect']!s:30s} suite: {suite:22s} hidden: {hidden:26s} {'OK' if good else 'UNEXPECTED'}")
            (HERE / f"{sid}.patch").write_text(diff)
            (HERE / f"{sid}.json").write_text(json.dumps({
                "id": sid, "issue": s["issue"], "defect": s["defect"], "expected_verdict": s["expected"],
                "expected_issue_type": s["issue_type"], "description": s["desc"], "how_to_find": s["how_to_find"],
                "branch": f"seeded/{sid.lower()}", "suite": suite, "hidden_tests": hidden, "hidden_failed": hfail}, indent=1))
            if push and good:
                run(["git", "-c", "user.name=seed-builder", "-c", "user.email=seed@users.noreply.github.com", "commit", "-q", "-m", f"seeded {sid}: {s['defect'] or 'correct control'} [skip ci]"], w)
                r = run(["git", "push", "-q", "--force", "origin", f"HEAD:refs/heads/seeded/{sid.lower()}"], w)   # explicit HEAD: a stale local branch of the same name must not be pushed instead
                print("   pushed" if r.returncode == 0 else "   push failed: " + r.stderr[-200:])
            run(["git", "worktree", "remove", "--force", str(w)], REPO)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main("--push" in sys.argv)
