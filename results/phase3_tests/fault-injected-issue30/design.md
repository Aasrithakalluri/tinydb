## Approach
Add a read-only `Table.is_empty()` in `tinydb/table.py` that returns `len(self) == 0`, reusing the existing `Table.__len__`, which reads through `_read_table()`. `db.is_empty()` needs no new code: `TinyDB.__getattr__` already forwards unknown attributes to the default table, so it reports on the default table, as `len(db)` does (ASM-02). Adding an explicit `TinyDB.is_empty` is not needed for the smallest change. The method is argument-free and returns a `bool`. No write path, query, or hash is touched. Tests cover table and database behaviour, including the empty, removed, and re-inserted cases. The never-written named table (Q-02) is designed as `True` (option a), per the assumption rule.

## Files to change
- `tinydb/table.py` :: `Table.is_empty` (new)
- `tests/test_tables.py` :: `test_is_empty` (new)
- `tests/test_tinydb.py` :: `test_default_table_is_empty` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected, no storage code is changed.
- Constraint 2 (`read()` returns `None` for empty storage, `write()` gets the full dict): not affected. `is_empty` only reads through the existing `_read_table()` path, which already handles `None`.
- Constraint 3 (middlewares): not affected.
- Constraint 4 (layering): respected. The change is inside `table.py`, which already owns table behaviour. No new imports, and `queries.py` and `database.py` are unchanged.
- Constraint 5 (query hash and `_update_table`): respected. `is_empty` is not a query and adds no cache key. It performs no write, so it does not need `_update_table`, and the query cache is not touched.

## Risks
- ASM-02 / Q-01: `db.is_empty()` is delivered by attribute forwarding to the default table and gets no explicit method. If maintainers want a database-level method or a different table, this must be rejected in the PR. The `test_default_table_is_empty` test pins the assumed behaviour.
- Q-02 (ASSUMED option a): `db.table('never_written').is_empty()` returns `True`, because the table reads as empty. If the maintainers want an error instead, the implementation and FR-03-AC4 change.
- Q-03 / NFR-01: the "no regression" gate is assumed. The change is additive, so it should not break existing tests, but the full `tests/` suite must still be run before the PR is merged.