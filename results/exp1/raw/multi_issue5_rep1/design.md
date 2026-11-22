## Approach
The library never sorts results. `Table.__iter__` and `Table.search` return documents in the order of the storage dict, which is insertion order for memory storage and JSON files written without `sort_keys`. So a fresh session already looks ordered, while `sort_keys=True` can change the file order after reopen. The design adds one private helper in `tinydb/table.py` that yields `(doc_id, doc)` pairs sorted by the converted `document_id_class` value. `__iter__` (and so `all()`) and `search()` both use it, so the order comes from the ID and not from the storage's key order. Updates and removals keep dict key order, so they need no change beyond a test. The change is read-side only: no storage format, public signature, or write path changes. This follows ASSUMED interpretation ASM-01 (ascending numeric doc_id, which overrides `sort_keys` text order, i.e. Q-02 option "override"). Reviewers should reject this in the PR if they want Q-01 option (b) or (c) instead.

## Files to change
- `tinydb/table.py` :: `Table._docs_in_id_order` (new)
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_tables.py` :: `test_iter_and_search_follow_numeric_id_order` (new)
- `tests/test_tables.py` :: `test_update_and_remove_keep_relative_order` (new)
- `tests/test_tinydb.py` :: `test_order_survives_reopen_with_sort_keys` (new)

## Constraint check
- Constraint 1 (storage subclasses `Storage`, `read`/`write`): not affected; no storage class is added or changed.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): respected; the helper only reads through `_read_table()`, which already handles `None`.
- Constraint 3 (middlewares): not affected; no middleware code changes.
- Constraint 4 (layering): respected; `table.py` keeps its imports, and `queries.py` and `storages.py` are not touched.
- Constraint 5 (query hash identifies exactly what it matches; all table changes go through `_update_table`): respected; no query hash changes, and no table write path changes. `search()` caches the already-sorted list, which holds the same documents, so the cache key still identifies the matches. The cache is still cleared by `_update_table`.

## Risks
- ASSUMED ASM-01: "sensible" means ascending numeric doc_id. If the reporter meant most-recently-modified or a user sort key (Q-01 b/c), this change is wrong and FR-01 and FR-03 must be redone.
- Sorting changes the output of any existing test or user code that relies on storage key order when doc_ids were set out of order. Also, custom `document_id_class` values that are not orderable (Q-04, RSK-03) would raise `TypeError` in the helper; the helper should be checked against the test suite before merge.
- Sorting on every `all()`/`search()` call adds O(n log n) cost per uncached read. This is acceptable for TinyDB's scale, but it is not measured here.