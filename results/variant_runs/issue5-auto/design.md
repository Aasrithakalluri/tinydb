## Approach
The stored dict already keeps insertion order in memory, so `all()` and `search()` only change order when storage reorders keys. JSON written with `sort_keys=True` (a configuration already used in `tests/test_storages.py:33`) stores ids as strings, so they reload as 1, 10, 11, 2, ... and the order cannot be recovered from the file. The fix is to make `Table` sort results by numeric document id in one shared helper, used by both `__iter__` (which backs `all()`) and `search()`. Auto-assigned ids follow insertion order, so this matches ASM-01 for the normal case. Storages, `_read_table` and `_update_table` stay unchanged. The sort is applied before the search result is cached, so cached and fresh results agree.

## Files to change
- `tinydb/table.py` :: `Table._iter_sorted_items` (new)
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_tables.py` :: `test_all_order_numeric_after_update_and_remove` (new)
- `tests/test_tables.py` :: `test_search_order_matches_all` (new)
- `tests/test_storages.py` :: `test_json_order_after_reopen_sort_keys` (new)

## Constraint check
- Rule 1 (storages subclass `Storage`): not affected, no storage class is added or changed.
- Rule 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected, `_read_table` and the write path are not touched.
- Rule 3 (middlewares): not affected, no middleware code is changed.
- Rule 4 (layering): respected, the helper lives inside `table.py` and imports nothing new; `queries.py` is not touched.
- Rule 5 (query hash identifies what it matches): respected, the query hash and `is_cacheable` are unchanged. The cache key still identifies the same matches, and the cached list is now stored in the sorted order.
- Rule 5 (all changes go through `_update_table`): respected, no write path is added. Existing `_update_table` cache clearing still applies.

## Risks
- ASSUMED interpretation (ASM-01, insertion order): the implementation orders by numeric document id. These agree for auto-assigned ids. They differ if a caller inserts with explicit ids out of order. A reviewer should reject this in the PR if insertion order must hold for explicit ids too; that would need a different on-disk format.
- Behaviour change for callers who relied on the file's key order when `sort_keys` is set, and for custom `document_id_class` values that do not convert cleanly with `int()`. The helper should fall back to the raw key in that case. Q-01 and RSK-02 remain open for this.
- Q-04 is unconfirmed: the default JSON kwargs are assumed not to sort keys. The new reopen test covers both cases so that the result does not depend on that answer.