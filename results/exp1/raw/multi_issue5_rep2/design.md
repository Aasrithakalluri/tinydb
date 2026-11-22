## Approach
Today `Table.__iter__` and `Table.search` walk `_read_table()` in stored dict order. That is insertion order in memory, but `JSONStorage.write` passes `sort_keys=True` to `json.dumps`, so a reopened file gives string-sorted IDs (1, 10, 11, 2, ...). The change adds one private helper in `table.py` that yields `(doc_id, doc)` pairs sorted by numeric document ID (ASM-01). It falls back to the raw key when the ID cannot be converted (Q-05). `__iter__` and `search` both use it, so `all()`, iteration and `search()` agree. Storages, the query classes and `_update_table` stay untouched. Tests cover in-memory order, search consistency and a JSON reopen with `sort_keys=True`. Everything here follows ASM-01, so a human can reject it in the PR.

## Files to change
- `tinydb/table.py` :: `Table._sorted_doc_items` (new)
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_tables.py` :: `test_all_order_ascending_numeric_ids` (new)
- `tests/test_tables.py` :: `test_search_order_matches_all` (new)
- `tests/test_storages.py` :: `test_json_order_after_reopen_sort_keys` (new)

## Constraint check
- Constraint 1 (storage subclasses `Storage`, `read`/`write`): respected, no storage class is changed.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): respected, `_read_table` and the storage contract are unchanged. The helper only reorders what `_read_table()` returns, and an empty table still yields nothing.
- Constraint 3 (middlewares): not affected, no middleware is touched.
- Constraint 4 (layering): respected, the change is inside `table.py` and imports nothing new. `queries.py` is not touched.
- Constraint 5 (query hash identifies exactly what it matches): respected, the query hash and cache key are unchanged and the match predicate is unchanged. Only the order of returned documents changes. Cached lists are built from the sorted order, so cache hits return the same order as misses.
- "All table changes go through `_update_table`": respected, no write path is changed. The change is read-only.

## Risks
- ASM-01 may be wrong: the reporter may want insertion order, last-changed order or a field order (Q-01, RSK-02). If so, the helper's sort key is the only thing to change.
- Callers who relied on the file's key order under `sort_keys=True` see a different order. The change also adds a sort on each `search()` cache miss and each iteration, which costs O(n log n).
- `Table.get()` and other single-document lookups may still use a different order than `search()` (the review noted this). They are out of scope here and need a follow-up if the reporter wants them aligned.