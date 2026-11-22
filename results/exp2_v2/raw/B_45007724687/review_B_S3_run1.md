## Review: `count()` without a condition

**Verdict: changes.** The no-argument path counts documents across every table in the database, not just the table being called. The tests don't exercise that path, so the suite passes anyway.

**Main defect.** `Table.count(None)` now returns `sum(len(t) for t in self._storage.read().values())`. `storage.read()` returns all tables, so the sum includes every other table. I ran this:

- Table `a` with 2 docs, table `b` with 3 docs.
- `a.count()` returns **5**. `len(a)` returns **2**.
- `a.count(None)` also returns 5.

The design said to use `len(self)`, which goes through `_read_table()` and is scoped to the table. The implementation does not do that. Replacing the body with `return len(self)` would fix it.

**Tests do not cover the change.** The diff adds only four FR-02 tests, all for `count(cond)`. None of the FR-01 (no-argument) or FR-03 (`count(None)`) acceptance criteria are tested. The builder summary says it added ten tests named `test_fr_01_ac1_…` through `test_fr_03_ac2_…`, and the test report says all ten criteria are covered. Neither matches the diff. The new tests would also have caught the bug above if they existed, since FR-01-AC1 and AC3 only use one table.

**Other discrepancies.**
- The builder summary says `tinydb/` was not touched and that the tests passed against the existing implementation. The diff changes `tinydb/table.py`, so the summary is wrong on that point.
- The test file has runs of blank lines before and after the added tests. That is cosmetic.
- I ran `python -m pytest -q` and got 236 passed. The test report says 248. The checkout may not match the report's run.

**What is fine.** The `cond=None` default keeps `count(cond)` on the `len(self.search(cond))` path, so FR-02 behaviour is unchanged. Explicit `None` now returns the total instead of raising. The spec left that open as Q-01, and the diff does not flag it, which is a reasonable thing to resolve later.

```json
{"verdict": "changes",
 "issue_type": "code",
 "tests_run": true,
 "findings": [
  {"file": "tinydb/table.py", "line": 719, "problem": "The no-argument path sums document counts over every table in storage, so count() on one table returns the total across all tables. It should use the table's own document count (len(self) / _read_table()).", "evidence": "Two tables, a with 2 docs and b with 3 docs: a.count() returns 5 and len(a) returns 2. a.count(None) also returns 5."},
  {"file": "tests/test_tables.py", "line": 200, "problem": "No test covers the new no-argument path (FR-01) or count(None) (FR-03). The four added tests only cover count(cond), which is unchanged, so the suite passes despite the bug. The builder summary and test report claim ten tests including FR-01 and FR-03, which the diff does not contain.", "evidence": "Diff adds only test_fr_02_ac1..ac4. No call to count() or count(None) without a condition appears in the test diff."},
  {"file": "tests/test_tables.py", "line": 200, "problem": "Runs of blank lines were left before and after the new tests.", "evidence": "Diff shows about ten empty lines before the first new test and four after the last."}
 ],
 "notes": [
  "The builder summary says tinydb/ was not touched, but the diff changes tinydb/table.py. The summary is inaccurate.",
  "python -m pytest -q reported 236 passed here; the test report says 248. The checkout may not match the report's run.",
  "Explicit count(None) now returns the total rather than raising. Q-01 in the spec is still open and the PR does not mention it.",
  "Changing the body to return len(self) would fix the cross-table bug. Tests for FR-01-AC1..AC4 and FR-03-AC1..AC2 should be added so that case is caught."
 ]}
```