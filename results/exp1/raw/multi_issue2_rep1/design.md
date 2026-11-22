## Approach
`Table.search` currently caches `docs[:]` and returns `docs`, and the hit path returns `cached_results[:]`. Both paths hand out the same document dicts that the cache holds. The change is in `Table.search` only. On a miss, store a deep copy in the cache and return a separate deep copy of the matches. On a hit, return a deep copy of the cached list. Per the ASSUMED interpretation (ASM-01 and Q-01 option a), results become independent deep copies. The cache key, query hashing, storage format and `_update_table` are untouched. The stale docstring is rewritten, and the test that asserts sharing is replaced with tests that mutate both the miss result and the hit result. Open questions are resolved by this assumption and listed under Risks for human rejection.

## Files to change
- `tinydb/table.py` :: `Table.search`
- `tinydb/table.py` :: `Table` (module import of `copy`, new import line)
- `tests/test_tinydb.py` :: `test_query_cache_documents_are_shared_with_cache` (rewrite: assert isolation instead of sharing)
- `tests/test_tinydb.py` :: `test_search_miss_result_mutation_is_isolated` (new)
- `tests/test_tinydb.py` :: `test_search_hit_result_mutation_is_isolated` (new)
- `tests/test_tinydb.py` :: `test_search_mutation_does_not_change_storage` (new)

## Constraint check
- Constraint 1 (storage subclassing): not affected; no storage class is added or changed.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected; `search` only reads through the existing `_read_table` path and never writes.
- Constraint 3 (middlewares): not affected; no middleware code is touched.
- Constraint 4 (layering): respected. `copy` is stdlib, `table.py` already imports stdlib, and `queries.py` and `storages.py` are not changed.
- Constraint 5 (hash identifies exactly what it matches): respected. The cache key and `is_cacheable()` logic stay the same, and only the stored and returned objects are copied, not the key. Table modification still goes through `_update_table`; `search` makes no table change.

## Risks
- ASSUMED contract (Q-01 option a, ASM-01 deep copy, Q-02): results are deep copies. If the maintainer picks option b (read-only documentation), this change is rejected and the docstring stays. Q-03 and Q-05 are also assumed: "stored data" means the file and in-memory table, and an equal-but-new query counts as a cache hit, since the cache key is unchanged.
- Performance (RSK-01, Q-04 unanswered): deep copying on every hit and miss slows `search()` on large tables. No limit was given, so this is accepted for now and should be measured before merge.
- Test coverage (RSK-02 and RSK-03): the new tests mutate the miss result, not only the hit result, so the reported first-search scenario is covered. Whether `MemoryStorage` returns shared dict objects from `_read_table` is unverified, so the miss-path copy is needed for that case too.