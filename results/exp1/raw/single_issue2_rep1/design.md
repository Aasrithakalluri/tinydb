## Approach
The root cause is in `Table.search` (`tinydb/table.py:249-297`). On a cache miss, it caches `docs[:]`, a shallow copy of the list, so the cache holds the same `Document` objects that the caller receives. A `Document` is a dict subclass built with a shallow copy of the top level, so nested lists (for example `tags`) are also shared with the storage backend for `MemoryStorage`. On a cache hit, `cached_results[:]` has the same problem.

Intended change (not applied, see Risks): store `copy.deepcopy(docs)` in the cache on a miss, and return `copy.deepcopy(cached_results)` on a hit. The first caller then gets objects that the cache does not share. The docstring at `tinydb/table.py:249-261` would be updated to match.

Status: this change is blocked. The existing test `test_query_cache_documents_are_shared_with_cache` (tests/test_tinydb.py:732-753) asserts that mutating a nested value of a search result changes the next search. Applying the change would fail that test. Per the rule against weakening existing tests, I did not change `tinydb/table.py` and did not edit or delete that test. The new tests in `tests/test_search_result_isolation.py` cover the issue's criteria. The five that expose the bug are `strict` xfail with the reason "BLOCKED CNF-01". Once a maintainer decides (Q-01), the `xfail` markers should be removed and the conflicting test resolved.

## Files to change
- `tinydb/table.py` :: `Table.search` (intended change, blocked by CNF-01, not applied)
- `tests/test_search_result_isolation.py` :: `test_fr_01_ac1_top_level_value_change` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_01_ac2_added_key` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_01_ac3_file_unchanged` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_02_ac1_nested_list_append` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_02_ac2_nested_mutation_reaches_storage` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_02_ac3_nested_mutation_on_cache_hit` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_03_ac1_list_append` (new)
- `tests/test_search_result_isolation.py` :: `test_fr_03_ac2_list_clear_on_cache_hit` (new)

## Constraint check
- Rule 1 and 2 (storages): not touched.
- Rule 3 (middlewares): not touched.
- Rule 4 (layering): the intended change uses only the standard library `copy` module in `table.py`. No new imports between package modules.
- Rule 5 (query hash): unchanged. Only the returned and cached document objects change, not the hash or the cache key.
- Writes still go through `Table._update_table`, which still clears the cache.
- ARCHITECTURE.md ADR-3 says "Cached documents are shared with the caller." That statement describes the current behaviour and would need updating with the fix. It is outside the files I may edit, so it is noted here only.

## Risks
- CNF-01: the fix contradicts an existing test that asserts the bug. Resolving it needs a maintainer decision (Q-01). Until then the issue is not fixed in code.
- Performance: deep copies on every search, including cache hits, increase memory and time for large result sets.
- Coverage: the tests check the criteria named in the spec. Other nested types (sets, custom objects) are not covered.
- The suite passes with `231 passed, 5 xfailed`. The xfail markers hide the bug until the decision is made, so they must be removed with the fix.