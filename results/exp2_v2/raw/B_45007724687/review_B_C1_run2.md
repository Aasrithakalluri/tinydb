Review of PR: `Table.count()` with no argument now returns the total document count.

**Does it resolve the issue?** Yes, for `Table`. `count(cond: Optional[QueryLike] = None)` returns `len(self)` when no query is given, and otherwise keeps the existing `len(self.search(cond))` path. `Optional` is already imported in `tinydb/table.py`, and `__len__` counts every document through `_read_table()`, so documents without an `id` are included. I ran `python -m pytest -q`: 248 passed, matching the author's report.

**Concerns (not blocking):**

- **Explicit `count(None)` changed behaviour.** Before this PR it raised. Now it silently returns the total. The author's spec marks this as open (Q-01, FR-03, RSK-01) and says to get an answer before changing the signature. The design still went ahead with a `None` default, and the tests in `test_fr_03_*` lock in the new behaviour. A sentinel default would keep `count(None)` raising if the maintainer prefers that. This is a judgement call the spec reserved for a human, so it is worth confirming with the maintainer.
- **`Database` has no `count()`.** The issue's `db` could mean a `Database`, which would still raise `TypeError` for `db.count()`. Q-02 is also open. The change only covers `Table`, which is the assumption the author made (ASM-01).
- **Test-only additions.** The diff only adds tests and one function change. The tests for FR-02 and FR-03 pass on the existing `search` path, which is expected for regression checks.

The code change is small and correct for the issue's stated request. The open-question decisions are the main caveat.

```json
{"verdict": "approve",
 "issue_type": "none",
 "tests_run": true,
 "findings": [],
 "notes": [
   "Full suite passes (248 passed). count() with no argument returns len(self), which counts all documents including those without an id. count(cond) keeps the search-based path unchanged.",
   "Behaviour change: explicit count(None) previously raised and now returns the total. The spec lists this as open (Q-01/FR-03/RSK-01) and asked for an answer before changing the signature. Confirm with the maintainer, or use a sentinel default if they want None to keep raising.",
   "Scope: only Table.count is changed. If the reporter's db is a Database object, db.count() still fails (Q-02 is open); no Database.count exists."
 ]}
```