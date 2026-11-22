## Approach
`Table.count` already takes an optional `cond`. When `cond` is `None` it returns `len(self)`, which reads the table without using the query cache. Otherwise it returns `len(self.search(cond))`. `TinyDB` forwards `count` to the default table through `__getattr__`, so `db.count()` reaches the same code. The change makes `count()` with no argument return the total and keeps the query path unchanged. The tests in `tests/test_count.py` cover FR-01 and FR-02 acceptance criteria and pass with the current working tree. The smallest change is to the `Table.count` signature and docstring so that no-argument use is the documented behaviour.

## Files to change
- `tinydb/table.py` :: `Table.count`
- `tests/test_count.py` :: `test_fr_01_ac1_count_without_argument_returns_total` (new)
- `tests/test_count.py` :: `test_fr_01_ac2_count_empty_table_returns_zero` (new)
- `tests/test_count.py` :: `test_fr_01_ac3_count_without_argument_after_remove` (new)
- `tests/test_count.py` :: `test_fr_01_ac4_count_explicit_none_returns_total` (new)
- `tests/test_count.py` :: `test_fr_02_ac1_count_with_query_counts_matches` (new)
- `tests/test_count.py` :: `test_fr_02_ac2_count_with_query_no_match_returns_zero` (new)
- `tests/test_count.py` :: `test_fr_02_ac3_count_with_query_missing_field_is_not_total` (new)

## Constraint check
- Layering (ARCHITECTURE.md section 3, rule 4): only `table.py` changes. No new imports, so `queries.py` and `storages.py` are untouched.
- Query hash rule (rule 5): `count` is read-only. It does not modify the table, so `_update_table` and the cache clear are not affected. Queries keep their hashes.
- Storage rules (rules 1–3): no storage or middleware change.

## Risks
- `count(None)` is ASSUMED to equal `count()` (ASM-01, Q-01). If maintainers want an error, `Table.count` must change and FR-01-AC4 must be removed.
- `len(self)` reads the table directly, so results may differ from a cached query only if the table is changed outside `Table`. This is the same limit that applies to every read in TinyDB.