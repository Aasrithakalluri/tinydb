## Approach
The order is fixed at read time, not at write time. `Table._read_table_sorted()` returns the raw `(doc_id, document)` pairs sorted by the document id converted with `self.document_id_class`, so numeric ids sort as numbers. Both `Table.__iter__` (used by `all()`) and `Table.search` read through this helper. Storage and the write path are not touched, so the stored order from history or from the JSON file no longer affects results. Cached search results are stored after sorting, so a cache hit returns the same order as a miss. The change is limited to read paths and needs no storage change.

## Files to change
- `tinydb/table.py` :: `Table._read_table_sorted`
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_document_order.py` :: `test_fr_01_ac1_all_sorted_after_explicit_ids` (new)
- `tests/test_document_order.py` :: `test_fr_01_ac2_empty_table_all_returns_empty` (new)
- `tests/test_document_order.py` :: `test_fr_02_ac1_search_sorted_by_id` (new)
- `tests/test_document_order.py` :: `test_fr_02_ac2_repeated_cached_search_same_order` (new)
- `tests/test_document_order.py` :: `test_fr_02_ac3_search_no_match_returns_empty` (new)
- `tests/test_document_order.py` :: `test_fr_03_ac1_update_keeps_id_order` (new)
- `tests/test_document_order.py` :: `test_fr_03_ac2_reopen_json_keeps_id_order` (new)
- `tests/test_document_order.py` :: `test_fr_03_ac3_sort_keys_json_numeric_id_order` (new)
- `tests/test_document_order.py` :: `test_fr_03_ac3_memory_storage_numeric_id_order` (new)

## Constraint check
- CON-01 (no dependencies): PASS. Only the built-in `sorted` is used.
- CON-02 (storage interface and `_update_table` unchanged): PASS. No storage or write-path code is edited.
- ARCHITECTURE §3 constraint 4 (layering): PASS. The change stays inside `table.py`; `queries.py` is not touched.
- ARCHITECTURE §3 constraint 5 (query hash and cache clearing): PASS. Query hashes and `_update_table` cache clearing are unchanged.
- ARCHITECTURE §3 constraint 2 (`read()` returns the full dict): PASS. The helper only reads the dict that `read()` returns.

## Risks
- RSK-01 (Q-01): if the author wanted insertion order, this change enforces the wrong order. Tests assume option (a).
- RSK-02: an uncached search now sorts its results, O(n log n). Cached repeats are unaffected.
- A custom `document_id_class` whose ids cannot be built from the stored string key would raise during sorting. The default `int` path is the only one tested.