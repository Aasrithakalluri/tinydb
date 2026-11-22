The PR doesn't work for multi-table databases, so I'm requesting changes.

**What the issue needs:** `count()` with no arguments should return the number of documents in that table. `count(query)` should keep working as before.

**What I checked**
- **Architecture:** I read `ARCHITECTURE.md`. Constraint 2 says `read()` returns the full `{table_name: {doc_id: doc}}` dict. The new code at `tinydb/table.py:~719` sums `len(t)` over every table in that dict (`.values()`). It never selects `self.name`. The change adds no write path and no query hash, so constraints 4 and 5 aren't affected.
- **Tests:** `python -m pytest -q` passes, 236 tests. None of the new tests call `count()` with no argument, so the new code path is untested. All four new tests only check the `count(cond)` path that already worked.
- **Experiment 1:** two tables, `a` with 1 document and `b` with 2.
  - `a.count()` returned 3 and `b.count()` returned 3.
  - `len(a)` returned 1, which is correct.
  - Expected: 1 and 2.
- **Experiment 2:** `count()` on an empty database returned 0, which is correct.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/table.py", "line": 719, "problem": "count() with no condition sums documents across ALL tables in the storage instead of only this table. Fix: use len(self._read_table()) or len(self).", "evidence": "python -c with MemoryStorage: a=db.table('a') (1 doc), b=db.table('b') (2 docs). Output was `a.count()` -> 3, `b.count()` -> 3, `len(a)` -> 1. Expected 1 and 2."}, {"file": "tests/test_tables.py", "line": 200, "problem": "No test calls count() without a condition, so the new behaviour is untested. The added tests only cover count(cond), which already worked.", "evidence": "The new tests test_fr_02_ac1 to ac4 all pass a condition. The suite passes with 236 tests despite the defect."}], "notes": ["count() on an empty database returned 0, which is correct.", "The new tests also add several stray blank lines in tests/test_tables.py."]}
```