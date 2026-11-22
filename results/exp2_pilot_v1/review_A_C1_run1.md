I approve this change. `count()` with no argument now returns the total number of documents, and `count(query)` behaves as before.

- **Expected behaviour from the issue:** `count()` with nothing passed returns the table's document count. `count(some_query)` is unchanged. The count is per table, because `Database.__getattr__` forwards to the default table.
- **Diff and context:** `Table.count` in `tinydb/table.py:709` now treats `cond=None` as "count everything" and returns `len(self)`. `Table.__len__` returns `len(self._read_table())`, so it reads the table directly and doesn't use the query cache.
- **Architecture:** `ARCHITECTURE.md` does not exist in this checkout, so I could not check section 3. I checked the constraints it names by reading the code instead:
  - The change is a read-only path in `Table`, so there is no layering issue.
  - It adds no query hash and no write, so the `_update_table` constraint doesn't come into play.
- **Test suite:** `python -m pytest -q` reported 230 passed.
- **Experiments:** I ran these against a JSON-backed `TinyDB`.
  - `count()` on an empty table returned 0.
  - After inserting `{'a':1}` and `{}`, `count()` returned 2, so documents without the field are counted. `count(where('a')==1)` returned 1.
  - After inserting another matching document, the same query returned 2 and `count()` returned 3.
  - After `remove(where('a')==1)`, the repeated query returned 0 and `count()` returned 1. The cached query is not stale after a write.
  - `count(None)` also returns the total. This follows from the new default and is harmless.
- **Added tests:** `tests/test_seed_c1.py` covers the empty table, documents with and without fields, and separate tables.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["ARCHITECTURE.md does not exist in this checkout, so section 3 could not be checked; constraints were checked by reading the code instead.", "count(None) is now equivalent to count().", "The docstring for count does not mention the optional behaviour; this is cosmetic."]}
```