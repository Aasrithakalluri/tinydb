## Approach
`Table.search()` currently returns `Document` objects that are shared with `_query_cache`. `Document` is only a shallow `dict` copy, so nested values are shared with the storage data too. The fix is to make `search()` return deep copies on both a cache miss and a cache hit, and to store a deep copy in the cache, so a caller's changes never reach the cache or the table data. The cache key (`cond` hash) and the matching logic stay as they are. The change is limited to `Table.search` and its docstring, plus tests in `tests/test_tables.py`. `all()`/`get()` are left unchanged (ASM-02 below). The copy is made with `copy.deepcopy` from the standard library, so `table.py` gains only an `import copy`.

Note: `MemoryStorage.read()` returns `self.memory` directly (tinydb/storages.py:177-178), so without a copy a nested mutation during `search()` would also change the stored data, even with no cache. The deep copy covers this case too.

## Files to change
- `tinydb/table.py` :: `Table.search`
- `tinydb/table.py` :: `import copy` (new)
- `tests/test_tables.py` :: `test_search_results_isolated_from_caller_mutation` (new)
- `tests/test_tables.py` :: `test_search_cache_isolated_nested_values` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected. No storage is changed.
- Constraint 2 (`read()` returns `None` when empty; `write()` gets the full dict): not affected. `_read_table` and `_update_table` are unchanged; the copy is applied only to the returned documents.
- Constraint 3 (middlewares): not affected. No middleware is changed.
- Constraint 4 (layering): respected. `table.py` gains only the stdlib `copy` import. `queries.py` and `storages.py` are not touched, and `table.py` still uses queries only through `QueryLike`.
- Constraint 5 (query hash identifies exactly what it matches): respected. `Query` hashes and `is_cacheable()` are unchanged, and the cache key remains `cond`. Only the stored and returned values are copied, not the key. No table modification is added, so `_update_table` and cache clearing are unchanged.

## Risks
- ASSUMED (Q-01 option a, Q-05): every `search()` result is an independent deep copy, and the scope is `search()` only. `all()` and `get()` are not changed, although `all()` also goes through `__iter__`. A human should reject this in the PR if `all()`/`get()` must also be protected (FR-02).
- ASSUMED (Q-03): "the same query" means an equal hash, which is the current cache behaviour. Queries with equal hashes keep sharing one cache entry, and that entry is always a private deep copy.
- Performance (RSK-02, Q-04): `deepcopy` on every `search()` (hit and miss) adds overhead proportional to result size. No threshold is set. The tests check correctness only, so a timing comparison on a large table is a follow-up item for the maintainers.