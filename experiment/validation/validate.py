#!/usr/bin/env python3
"""Validate the hidden tests: two independently written fixes per issue must pass them.

For every issue there is a *reference* fix (A) and an *alternative* fix (B) that uses a different approach.
Each is applied to a clean worktree of the baseline commit; we run the hidden tests of that issue and the
repository's own suite. A hidden test set is only trusted if A passes it, B passes it (or fails only a test
deliberately marked `extra`), and the baseline fails it.

Usage: python experiment/validation/validate.py   (needs ~/a3_private/hidden_tests and a venv with pytest)
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = "edff96aeb2616402e9489d46e90a592c05565621"
HIDDEN = Path.home() / "a3_private" / "hidden_tests"
OUT = Path(__file__).resolve().parent
PY = sys.executable


def edit(path: Path, old: str, new: str, count: int = 1):
    s = path.read_text()
    assert old in s, f"pattern not found in {path.name}: {old[:60]!r}"
    path.write_text(s.replace(old, new, count))


# ----------------------------------------------------------------------------- fixes
def i1_A(w):   # explicit result for paths that cannot be resolved; only != returns True
    q = w / "tinydb/queries.py"
    edit(q, "            allow_empty_path: bool = False\n    ) -> QueryInstance:", "            allow_empty_path: bool = False,\n            missing_result: bool = False\n    ) -> QueryInstance:")
    edit(q, "            except (KeyError, TypeError):\n                return False", "            except (KeyError, TypeError):\n                return missing_result")
    edit(q, "            ('!=', self._path, freeze(rhs))\n        )", "            ('!=', self._path, freeze(rhs)),\n            missing_result=True\n        )")

def i1_B(w):   # != is defined as the negation of ==
    edit(w / "tinydb/queries.py", "        return self._generate_test(\n            lambda value: value != rhs,\n            ('!=', self._path, freeze(rhs))\n        )", "        return ~(self == rhs)")

def i2_A(w):   # deep-copy on the way into the cache and on the way out
    t = w / "tinydb/table.py"
    edit(t, "from collections.abc import Callable", "import copy\nfrom collections.abc import Callable")
    edit(t, "            return cached_results[:]", "            return copy.deepcopy(cached_results)")
    edit(t, "            self._query_cache[cond] = docs[:]", "            self._query_cache[cond] = copy.deepcopy(docs)")

def i2_B(w):   # the cache keeps only document ids; hits are rebuilt from storage
    t = w / "tinydb/table.py"
    edit(t, "from collections.abc import Callable", "import copy\nfrom collections.abc import Callable")
    edit(t, "            return cached_results[:]", "            table = self._read_table()\n            return [self.document_class(copy.deepcopy(table[str(i)]), self.document_id_class(i))\n                    for i in cached_results if str(i) in table]")
    edit(t, "            self._query_cache[cond] = docs[:]", "            self._query_cache[cond] = [d.doc_id for d in docs]")
    edit(t, "            for doc_id, doc in self._read_table().items()\n            if cond(doc)\n        ]", "            for doc_id, doc in self._read_table().items()\n            if cond(doc)\n        ]\n        docs = [self.document_class(copy.deepcopy(dict(d)), d.doc_id) for d in docs]")

def i3_A(w):
    t = w / "tinydb/table.py"
    edit(t, "    def count(self, cond: QueryLike) -> int:", "    def count(self, cond: Optional[QueryLike] = None) -> int:")
    edit(t, "        return len(self.search(cond))\n", "        if cond is None:\n            return len(self)\n        return len(self.search(cond))\n")

def i3_B(w):
    t = w / "tinydb/table.py"
    edit(t, "    def count(self, cond: QueryLike) -> int:", "    def count(self, cond=None) -> int:")
    edit(t, "        return len(self.search(cond))\n", "        return sum(1 for _ in self) if cond is None else len(self.search(cond))\n")

def i4_A(w):
    edit(w / "tinydb/operations.py", "def subtract(", "def multiply(field: str, n: Union[int, float]) -> Callable[[MutableMapping], None]:\n    \"\"\"\n    Multiply a given field in the document by ``n``.\n    \"\"\"\n    def transform(doc: MutableMapping):\n        doc[field] *= n\n\n    return transform\n\n\ndef subtract(")

def i4_B(w):
    edit(w / "tinydb/operations.py", "def subtract(", "def multiply(field, n):\n    \"\"\"Scale a numeric field by the factor ``n``.\"\"\"\n    def transform(doc):\n        doc[field] = doc[field] * n\n\n    return transform\n\n\ndef subtract(")

def i5_A(w):   # sort where documents are produced (__iter__, search) and where ids are returned (update)
    t = w / "tinydb/table.py"
    edit(t, "        for doc_id, doc in self._read_table().items():\n            # Convert documents to the document class", "        for doc_id, doc in sorted(self._read_table().items(), key=lambda kv: int(kv[0])):\n            # Convert documents to the document class")
    edit(t, "            for doc_id, doc in self._read_table().items()\n            if cond(doc)", "            for doc_id, doc in sorted(self._read_table().items(), key=lambda kv: int(kv[0]))\n            if cond(doc)")
    edit(t, "            return updated_ids", "            return sorted(updated_ids)", 3)

def i5_B(w):   # sort once, where the table is read from storage
    t = w / "tinydb/table.py"
    edit(t, "        # Retrieve the current table's data\n        try:\n            table = tables[self.name]", "        # Retrieve the current table's data\n        try:\n            table = dict(sorted(tables[self.name].items(), key=lambda kv: int(kv[0])))")

FIXES = {1: (i1_A, i1_B), 2: (i2_A, i2_B), 3: (i3_A, i3_B), 4: (i4_A, i4_B), 5: (i5_A, i5_B)}


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def pytest(w, target):
    r = run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov", "-c", "/dev/null", str(target)], w)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    failed = re.findall(r"FAILED \S*::(\w+)", r.stdout)
    return last, failed


def main():
    rows = []
    tmp = Path(tempfile.mkdtemp(prefix="validate-"))
    try:
        for n, (a, b) in FIXES.items():
            hidden = HIDDEN / f"test_issue{n}_hidden.py"
            for label, fix in (("baseline", None), ("A", a), ("B", b)):
                w = tmp / f"w{n}{label}"
                run(["git", "worktree", "add", "-q", "--detach", str(w), BASE], REPO)
                if fix:
                    fix(w)
                    run(["git", "add", "-A"], w)
                    diff = run(["git", "diff", "--cached"], w).stdout
                    (OUT / f"issue{n}_{label}.patch").write_text(diff)
                h_sum, h_failed = pytest(w, hidden)
                s_sum, s_failed = pytest(w, w / "tests")
                rows.append(dict(issue=n, fix=label, hidden=h_sum, hidden_failed=h_failed, suite=s_sum, suite_failed=s_failed))
                print(f"issue {n} {label:8s} hidden: {h_sum:28s} suite: {s_sum}")
                run(["git", "worktree", "remove", "--force", str(w)], REPO)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    (OUT / "results.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
