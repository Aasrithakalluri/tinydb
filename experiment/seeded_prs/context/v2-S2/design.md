## Approach
`Table.search()` hands out the same document objects that the query cache holds, and on a cache miss it caches the very objects it returns. On the `MemoryStorage` path, `storage.read()` also returns the live stored dicts, so a mutation can reach the stored data itself. The fix is to make `search()` return deep copies on both the hit and miss paths, and to store a separate deep copy in the cache, so neither the cache nor storage can be reached through a returned document. Cache keys, `_update_table`, and `clear_cache()` stay as they are. The spec is NOT READY, so this design assumes the deep-copy contract (option b in Q-01) and records that as a risk. The existing test that asserts sharing must be rewritten to match.

## Files to change
- `tinydb/table.py` :: `Table.search`
- `tinydb/table.py` :: `Table.__init__` (no change expected; only if the cache type annotation needs adjusting; leave untouched unless required)
- `tests/test_tinydb.py` :: `test_query_cache_documents_are_shared_with_cache`
- `tests/test_tinydb.py` :: `test_search_results_isolated_from_cache` (new)

Note: the second `tinydb/table.py` line above is optional and should be dropped if the implementer does not need it. The final list the implementer should act on is:
- `tinydb/table.py` :: `Table.search`
- `tests/test_tinydb.py` :: `test_query_cache_documents_are_shared_with_cache`
- `tests/test_tinydb.py` :: `test_search_results_isolated_from_cache` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected; no storage changes.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected; `_update_table` and the storage contract are unchanged.
- Constraint 3 (middlewares): not affected.
- Constraint 4 (layering): respected; the only addition is the stdlib `copy` import in `table.py`. `queries.py` and `storages.py` are untouched.
- Constraint 5 (query hash identifies exactly what it matches): respected; no query or hash code changes, and cache keys stay the same. Only the stored and returned values are copied.
- Constraint 5 (all table modifications go through `_update_table`, which clears the cache): respected; no write path changes, so `clear_cache()` still runs after every write.
- ARCHITECTURE.md ADR-3 consequence "Cached documents are shared with the caller": this design changes that consequence, so the ADR text should be updated to say results are copies.

## Risks
- Deep-copying every returned document on every search, including cache hits, costs CPU and memory on large results (RSK-01). The cost is unmeasured, so a benchmark should be run before merging.
- The contract is not decided (Q-01, CNF-01). Callers who rely on mutating returned documents to update the cache will break. The docstring, the ADR-3 text, and the changelog need to say so.
- The fix must cover the miss path and the `MemoryStorage` path, where `storage.read()` returns live dicts. Testing only the cache-hit path would leave the bug in place (RSK-03, FR-01-AC3).