## Review: PR #5 (sort results by doc_id)

**Verdict: changes.** The sort uses the raw dict key, not the document ID class, so results are misordered once there are 10 or more documents. The author's tests don't cover that case.

### Finding: the sort is lexicographic on string keys

`Table.__iter__` and `Table.search` sort with `key=lambda item: item[0]`. The design said the key should go through `document_id_class(...)` so that string keys such as "10" and "9" sort as integers. The diff does not do that.

I ran a check with 12 documents, both in a JSON file reopened from disk and in memory storage. Both return the same wrong order:

- reopened JSON `all()`: `[1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9]`
- JSON `search(lambda d: True)`: same order
- in-memory `all()`: same order

This is the same kind of misordering the issue describes, and it happens on every read path the PR touches. The FR-04 tests only use 3 documents, so they cannot reveal it.

The fix is to sort on the converted ID, for example `sorted(..., key=lambda item: self.document_id_class(item[0]))`, or to sort the converted documents by `doc_id`. The same key should be used in both places. A regression test with 10 or more documents, checked after a JSON reopen, is needed.

### Other observations

- The builder's report says all 264 tests pass. My run of `python -m pytest -q` collected 241 tests and all passed, so the test count differs from the report. I did not dig into why.
- The builder notes that the new tests pass on the unmodified code path. That is not quite accurate for this diff. The tests pass here because the cases they check happen to sort correctly as strings. They do not show the fix works in general.
- The spec's RSK-01 remains open: the reported misordering was never reproduced, so this change is not shown to fix the reported bug. This is noted, not counted against the diff.
- The per-call O(n log n) sort cost (Q-04) and the change in insertion order for existing users (RSK-04) are disclosed in the design. Both are acceptable to note for a human reviewer.

```json
{"verdict": "changes",
 "issue_type": "code",
 "tests_run": true,
 "findings": [
  {"file": "tinydb/table.py", "line": 740, "problem": "Table.__iter__ sorts on the raw dict key (item[0]) instead of the converted document ID, so string keys from JSON storage sort lexicographically. Results are misordered once there are 10 or more documents.", "evidence": "Reopened JSON db with 12 inserts: all() and search() return [1, 10, 11, 12, 2, 3, ..., 9]. In-memory db gives the same order. The design required document_id_class(...) in the sort key."},
  {"file": "tinydb/table.py", "line": 272, "problem": "Table.search has the same raw-key sort, so search results are misordered in the same way.", "evidence": "db.search(lambda d: True) on the 12-document JSON db returns [1, 10, 11, 12, 2, ..., 9]."},
  {"file": "tests/test_tinydb.py", "line": 840, "problem": "FR-04 tests use only 3 documents, so they cannot catch the lexicographic ordering bug. No test covers 10 or more documents.", "evidence": "The tests insert 3 docs (and 3 with one removed). The bug appears at 10 docs, e.g. 1, 10, 11, 12, 2."},
  {"file": "tests/test_tables.py", "line": 202, "problem": "The builder's report says 264 tests pass; my run collected 241 tests, all passing. The reported count does not match this checkout.", "evidence": "python -m pytest -q: 241 passed."}
 ],
 "notes": [
  "The spec's RSK-01 still applies: the reported misordering was never reproduced, so this change is not shown to fix the reported bug.",
  "Per-call sort cost (Q-04) and the change in insertion order for existing users (RSK-04) are disclosed and need a human decision.",
  "The builder's claim that the new tests confirm the behaviour is weaker than it sounds: they pass because the small cases happen to sort correctly as strings."
 ]}
```