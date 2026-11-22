Approve. `count()` with no argument now returns the total number of documents, and `count(some_query)` behaves as before.

**What I checked**
- **The change:** `Table.count` now takes `cond=None` and returns `len(self)` in that case. `len(self)` is `len(self._read_table())`, so it reads straight from storage and doesn't touch the query cache.
- **ARCHITECTURE.md, section 3:**
  - The change is entirely in `table.py`, so layering (constraint 4) is respected.
  - No query objects or hashes are created or changed, so constraint 5 on query hashes doesn't apply.
  - The new path does not write, so the "writes go through `_update_table`" rule has nothing to apply to.
- **Closest analogue:** `Table.__len__` and `TinyDB.__len__` give the same total, and `TinyDB.__getattr__` forwards `count` to the default table. I did not find a sibling method that handles `None` differently.
- **Test suite:** `python -m pytest -q` gave 248 passed.
- **Experiments:** I ran these through `python -c`, once with `MemoryStorage` and once with a JSON-backed file.
  - `db.count()` on an empty database returned 0.
  - After inserting `{'a':1}` and `{'b':2}`, `db.count()` returned 2.
  - `db.count(where('a')==1)` returned 1.
  - `db.count(None)` returned 2.
  - After removing `{'a':1}`, `db.count()` returned 1, so the count reflects writes.
  - `db.table('x').count()` on a table that was never written returned 0.
  - With the JSON file, `count()` returned 1 after one insert, and a nonexistent table returned 0.
- **Existing tests:** the diff only adds tests; none were removed or rewritten.

**Notes**
- `count(None)` also returns the total. The issue doesn't ask for this, but it fits the `Optional` signature.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["count(None) also returns the total; not requested by the issue but consistent with the Optional signature.", "Tests only added, none removed or rewritten."]}
```