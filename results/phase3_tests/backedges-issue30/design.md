## Approach
Add a read-only `Table.is_empty()` that returns `len(self) == 0`, so it reuses the existing `Table.__len__` and returns a real `bool`. Add an explicit `TinyDB.is_empty()` that delegates to the default table, mirroring `TinyDB.__len__`, so `db.is_empty()` no longer depends on `__getattr__` forwarding (ASSUMED Q-01 option a). Nothing is written, so `_update_table`, the query cache, `queries.py` and storages stay untouched. The previous failure was an injected fault in `test_injected.py`, not in this design's code path; the revised plan changes no shared logic.

## Files to change
- `tinydb/table.py` :: `Table.is_empty` (new)
- `tinydb/database.py` :: `TinyDB.is_empty` (new)
- `tests/test_tables.py` :: `test_is_empty` (new)
- `tests/test_tinydb.py` :: `test_is_empty_default_table` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected, no storage is added or changed.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected, the method only reads through the existing `len(self)` path.
- Constraint 3 (middlewares): not affected, no middleware is touched.
- Constraint 4 (layering): respected; `table.py` uses only its own `__len__`, and `database.py` delegates to the default table through `self.table(...)` as `__len__` already does, with no new imports.
- Constraint 5 (query hash and `_update_table`): respected; the method is a read, adds no query, and does not modify the table, so no hash or cache invalidation changes.

## Risks
- Q-01 is assumed as option (a): `db.is_empty()` checks only the default table. If the maintainer rejects this, remove `TinyDB.is_empty` and its test, and the forwarding behaviour will apply.
- Q-02 is assumed as option (a): a never-written named table returns `True`, because `db.table(name)` creates no storage entry and `len` is 0. If option (b) is chosen, `Table.is_empty` must raise instead, and `test_is_empty` needs a matching case.
- Name collision: `TinyDB.is_empty` will shadow forwarding for any future `is_empty` added to the default table's behaviour. The full test suite should be rerun after the change, since the injected failure in `test_injected.py` is not a property of this design.