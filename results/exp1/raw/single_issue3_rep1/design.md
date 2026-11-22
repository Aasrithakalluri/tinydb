## Approach
`Table.count` gets an optional `cond` argument (default `None`). With no condition it returns `len(self)`, which reads the table through `_read_table()` and does not touch the query cache. This meets FR-01 and FR-03, and avoids the stale-cache risk in RSK-01. With a condition, the existing `len(self.search(cond))` path runs unchanged, which meets FR-02. `TinyDB.count` needs no change: `TinyDB.__getattr__` forwards `count` to the default table. The same `None` check covers `count(None)` (ASM-01). No writes are added, so `_update_table` and the cache clearing are untouched.

Tests live in a new `tests/test_count.py` and cover every acceptance criterion, using `MemoryStorage`.

## Files to change
- `tinydb/table.py` :: `Table.count`
- `tests/test_count.py` :: `make_db` (new)
- `tests/test_count.py` :: `test_fr_01_ac1_counts_all_documents` (new)
- `tests/test_count.py` :: `test_fr_01_ac2_empty_table_returns_zero` (new)
- `tests/test_count.py` :: `test_fr_01_ac3_docs_without_id_field_are_counted` (new)
- `tests/test_count.py` :: `test_fr_01_ac4_explicit_none_counts_all_documents` (new)
- `tests/test_count.py` :: `test_fr_02_ac1_query_count_unchanged` (new)
- `tests/test_count.py` :: `test_fr_02_ac2_query_matching_nothing_returns_zero` (new)
- `tests/test_count.py` :: `test_fr_03_ac1_count_reflects_insert_and_remove` (new)
- `tests/test_count.py` :: `test_fr_03_ac2_count_after_cached_query_is_not_stale` (new)

## Constraint check
- CON-01 (no dependencies): PASS. Standard library only; `Optional` was already imported in `table.py`.
- CON-02 (writes through `_update_table`, cache not stale): PASS. No write path is added. The total comes from `_read_table()`, not the query cache.
- ARCHITECTURE §3 rule 4 (layering): PASS. Only `table.py` changes; no new imports between modules.
- ARCHITECTURE §3 rule 5 (query hashes): PASS. No query is built or hashed for the no-condition case.

## Risks
- Behaviour change for `count(None)`: before, it reached `search(None)` and failed. It now returns the total (ASM-01, Q-01). Low impact; the test FR-01-AC4 records the choice.
- The full suite was run with `python -m pytest -q`: 236 passed. No existing test was changed.
- The branch was not created: git commands are not permitted in this session. The changes are in the working tree of `/home/runner/work/tinydb/tinydb`, not on a separate branch.