## Approach
Give `Table.count` a default for `cond` (`None`). When no query is given, return `len(self)`, which already counts every document in the table via `_read_table()`. Any real query keeps the existing `len(self.search(cond))` path, so `count(cond)` results do not change. The change is confined to `Table`, because the issue's `db` is treated as a `Table` (ASM-01). Q-01 (explicit `None`) and Q-02 (`Database.count`) remain open, so this design implements the no-argument form (FR-01) and the regression path (FR-02). It does not add `Database.count`, and it does not settle the explicit `None` behaviour for FR-03 until Q-01 is answered.

## Files to change
- `tinydb/table.py` :: `Table.count`
- `tests/test_tables.py` :: `test_count_without_condition` (new)

## Constraint check
- Constraint 4 (layering): respected. The change is inside `table.py` and uses only the existing `Table` methods. No new imports, and `queries.py` is not touched.
- Constraint 5 (query hash identifies exactly what it matches): respected. No query or hash is created for the no-argument call. The `cond` path still goes through `search(cond)` and keeps its existing hash.
- "All table changes go through `_update_table`": not applicable. `count` is read-only and does not modify the table or the cache.
- Constraint 2 (`Storage.read()` returns `None` when empty): respected. `__len__` already uses `_read_table()`, which handles the empty-storage case, so the no-argument path inherits that handling.
- Constraint 1 and Constraint 3 (storages and middlewares): not affected.

## Risks
- Q-01 is open. If the maintainer wants an explicit `count(None)` to keep raising, the `None` default must instead be a sentinel. This would change the signature and the tests for FR-03.
- Q-02 is open. If `Database` is also meant to get `count()`, a new method is needed in `tinydb/database.py`, and the reporter's code would still fail until that is added (RSK-02).
- Using `len(self)` for the no-argument path means it counts documents through `_read_table()`. This is correct for FR-01-AC3, which covers documents without `id`, but it has not been checked against the test suite.