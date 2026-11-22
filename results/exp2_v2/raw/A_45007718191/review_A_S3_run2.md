**Verdict: changes.** The no-argument `count()` counts documents in every table, not only the table it is called on.

**What the issue needs**
- `count()` with no arguments returns the number of documents in that table.
- `count(query)` behaves as before.

**Constraints checked** (ARCHITECTURE.md §3)
- Layering (constraint 4) is respected. `table.py` touches storage only through `read()`.
- Constraints 2 and 5 are not at risk, because `count()` does not write.
- Constraint 2 says `read()` returns the full `{table_name: {doc_id: doc}}` dict. The new code in `tinydb/table.py` (`count`, ~line 719) sums `len(t)` over all of that dict's values, which includes other tables.
- It ignores `self.name`, and the table's own accessor `self._read_table()` does the per-table lookup correctly.

**Tests**
- `python -m pytest -q` gives 236 passed.
- None of the four new tests calls `count()` without arguments, so the new branch is untested. They only exercise `count(cond)`, which already worked.

**Reproduction**
- I used a `MemoryStorage` database with table `a` holding 1 document and table `b` holding 2.
- `a.count()` returned 3, but `len(a)` is 1.
- `db.count()` also returned 3. The default table is empty, so it should be 0.
- A third, empty table `e` also returned `e.count() == 3`; it should be 0.
- The result is wrong whenever the database has more than one table.

**Suggested fix**
Use `len(self._read_table())`, or equivalent, in the `cond is None` branch. Add tests with several tables and with an empty table.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/table.py", "line": 719, "problem": "count() with no condition sums documents across ALL tables in storage instead of only this table's documents.", "evidence": "python -c with MemoryStorage: table a has 1 doc, table b has 2 docs. a.count() -> 3 (len(a) is 1), db.count() -> 3 (default table is empty), and an empty table e.count() -> 3."}, {"file": "tests/test_tables.py", "line": 200, "problem": "No test exercises count() without arguments, which is the issue's feature. The four new tests only cover count(cond), which already worked.", "evidence": "The new tests all call table.count(<cond>); the suite passes (236) while the bug above exists."}], "notes": ["Suggested fix: use len(self._read_table()) for the no-condition branch, and add multi-table and empty-table tests."]}
```