## Approach
`Table.search` (tinydb/table.py) now isolates the query cache from callers:
- On a cache miss, each matching document is deep-copied from the storage data before being wrapped in `Document`. This stops nested values from being shared with the storage's raw dict (relevant for `MemoryStorage`).
- The result is stored in the cache as a deep copy, so the returned documents and the cache do not share objects.
- On a cache hit, a deep copy of the cached list is returned.

Nothing else changes: the query hash, `_update_table`, `clear_cache`, the storage interface, and the existing `test_query_cache*` tests are unaffected. The `copy` module is imported at the top of `table.py`.

The existing test `test_query_cache_documents_are_shared_with_cache` asserted the reported bug (a mutated nested value reaching the cache). I changed only its document-level assertion to the new behaviour, and kept its list-level check. This needs human review (CNF-01).

Test status: `python -m pytest -q` reports 244 passed; `python -m compileall` succeeds.

## Files to change
- `tinydb/table.py` :: `Table.search`
- `tests/test_search_copies.py` :: `test_fr_01_ac1_repeat_search_after_mutation_returns_stored_data` (new)
- `tests/test_search_copies.py` :: `test_fr_01_ac2_no_match_result_mutation_not_cached` (new)
- `tests/test_search_copies.py` :: `test_fr_01_ac3_cache_hits_return_independent_objects` (new)
- `tests/test_search_copies.py` :: `test_fr_02_ac1_uncached_result_mutation_does_not_affect_next_search` (new)
- `tests/test_search_copies.py` :: `test_fr_02_ac2_result_mutation_does_not_change_storage` (new)
- `tests/test_search_copies.py` :: `test_fr_02_ac3_uncacheable_query_result_mutation_is_isolated` (new)
- `tests/test_search_copies.py` :: `test_fr_03_ac1_update_after_mutation_shows_updated_stored_value` (new)
- `tests/test_search_copies.py` :: `test_fr_03_ac2_remove_after_mutation_returns_empty_result` (new)
- `tests/test_tinydb.py` :: `test_query_cache_documents_are_shared_with_cache`

## Constraint check
- CON-01 / constraint 4 (layering): `copy` is standard library; no new import between package modules.
- Constraint 1 (storage interface): unchanged.
- Constraint 2 (`read()` returns None or the full dict): unchanged; `_read_table` is untouched.
- Constraint 3 (middlewares): not touched.
- Constraint 5 (query hash and `_update_table` clearing the cache): the hash and the write path are unchanged.
- ADR-3 consequence "cached documents are shared with the caller" is no longer true. `ARCHITECTURE.md` is outside the files I may write, so it needs a follow-up update (RSK-03).
- No dependencies added (CON-01).

## Risks
- Performance: a deep copy on every cache hit costs more for large results (RSK-01, Q-01).
- Non-copyable stored values (for example objects holding locks) would now raise in `search()` (RSK-02). Only `MemoryStorage` can hold such values; JSON storage cannot.
- The existing shared-document test was changed; a maintainer must confirm this (CNF-01).
- The branch for this issue was not created because git commands are not permitted in this session. The changes are in the working tree.
- The design is unchanged from the spec; FR-02 and FR-03 are inferred and need confirmation (Q-02, Q-03).