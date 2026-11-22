## Approach
Results come back in the storage dictionary's insertion order (`Table._read_table()` iterated directly). Updates keep a document's position, remove-and-reinsert moves it to the end, and explicit `Document` IDs can be added out of order, so the order is neither sorted nor stable across history. JSON reload keeps that order too. The smallest change that meets FR-01 to FR-03 under ASM-01 is to read the table items sorted by document ID (converted with `document_id_class`, so integer IDs sort numerically) in the two places that return documents to callers: `Table.__iter__` (used by `all()`) and `Table.search`. A small private helper `Table._sorted_table_items()` holds the sort. Storage format, the write path, the query cache and `get()` are unchanged. The query cache stores the already-sorted list, so cached results keep the same order.

## Files to change
- `tinydb/table.py` :: `Table._sorted_table_items` (new)
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_ordering.py` :: `module` (new)

## Constraint check
- CON-01 (no new dependencies): PASS. Only the standard library `sorted` is used.
- CON-02 (layering): PASS. No new imports; `table.py` still uses only `Storage` through the existing interface.
- CON-03 (writes through `_update_table`, cache cleared): PASS. No write path is changed.
- ARCHITECTURE.md §3 rule 1, 2, 3 (storage and middleware contracts): PASS. Storages, middlewares and the `read()`/`write()` contract are untouched.
- ARCHITECTURE.md §3 rule 5 (query hashes): PASS. Query hashing is unchanged. Cached results are the same ordered lists.
- Test status: `python -m pytest -q` gives 235 passed (228 existing + 7 new).

## Risks
- RSK-01 (from spec): existing callers that relied on insertion order will see a different order. Mitigation: Q-01 must be answered before release.
- RSK-02 (from spec): O(n log n) cost on each `all()`, `search()` and iteration. Not measured.
- RSK-03 (from spec): `get(cond)` still returns storage-order first matches; this is intentionally left unchanged (Q-04).
- Assumption ASM-01 is that ascending document ID is the wanted order. If the author wants insertion or last-modified order, `_sorted_table_items` must change and the FR-01 to FR-03 tests must be rewritten.
- No git branch was created, because git commands are not permitted in this session; the change is in the working tree.