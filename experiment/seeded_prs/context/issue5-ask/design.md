## Approach
Sort the documents by `doc_id` when the table reads them, instead of relying on the dict's stored order. The sort goes in `Table.__iter__`, which `Table.all()` already uses, and in `Table.search()` before the result is cached. Sorting on read makes the order independent of how the JSON file was written, so reopen behaviour (FR-04) follows automatically. Updates keep `doc_id` and therefore keep position (FR-03). Only the `table.py` read paths change. Storage, `_update_table`, and the query hash are untouched. The sort key uses `document_id_class(...)` so that string keys from JSON such as "10" and "9" sort as integers. Assumes ASM-02 (search uses the same order as all) and that sorting per call is acceptable (Q-04 open).

## Files to change
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_tables.py` :: `test_all_returns_ascending_doc_id` (new)
- `tests/test_tables.py` :: `test_search_returns_ascending_doc_id_after_lower_insert` (new)
- `tests/test_tables.py` :: `test_update_and_upsert_keep_position` (new)
- `tests/test_tinydb.py` :: `test_json_reopen_order_is_ascending` (new)

## Constraint check
- Constraint 1 (storage subclassing): not affected. No storage class is added or changed.
- Constraint 2 (`read()` returns `None` when empty; `write()` gets the full dict): not affected. `_read_table` and the write path are unchanged, and the sort only happens on the returned copy.
- Constraint 3 (middlewares): not affected. No middleware code is touched.
- Constraint 4 (layering): respected. Only `table.py` changes, and it uses only builtins (`sorted`). No new imports, and `queries.py` is not touched.
- Constraint 5 (query hash and `_update_table`): respected. The query and its hash are unchanged, and the match set is the same. Only the order of results changes. The cache stores the already sorted list, so a cached result has the same order as a fresh one. No write path is changed, so every write still goes through `_update_table` and clears the cache.

## Risks
- ASM-02 is unconfirmed: this design assumes `search()` uses the same order as `all()`. If the maintainer rejects that (Q-05 open), only the `search` change must be reverted.
- The misordering in the issue has not been reproduced (RSK-01). Sorting by `doc_id` may not be the cause of the reported bug, so the fix could leave it in place. Q-05 is still open, and the implementation does not wait for it.
- Sorting on every `all()` and `search()` call costs O(n log n) per call (Q-04 open), and users who relied on insertion order will see a different order (RSK-04). Both need to be noted in the pull request for a human to accept.