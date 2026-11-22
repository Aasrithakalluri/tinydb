## Approach
Give `Table.count` a default of `None` for `cond`. When no condition is passed, return `len(self)`, which already counts every stored document through `_read_table()`. When a query is passed, keep the existing `len(self.search(cond))` path unchanged. This is a small change in one method, with no new storage reads, no new query objects and no table writes. `TinyDB` forwards unknown attributes such as `count` to the default table, so `db.count()` should work without editing `database.py`. The spec leaves `count(None)` open (Q-01), so this design treats `None` the same as no argument (option a). That choice is listed under Risks.

## Files to change
- `tinydb/table.py` :: `Table.count`
- `tests/test_tables.py` :: `test_count_without_condition` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected, since no storage code changes.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected. The no-argument path goes through `__len__` and `_read_table()`, which the code already uses.
- Constraint 3 (middlewares): not affected, since no middleware code changes.
- Constraint 4 (layering): respected. Only `table.py` changes, and it gains no new imports beyond what the signature needs (`Optional` or `None` handling in the same module).
- Constraint 5 (query hash identifies exactly what it matches): respected. The no-argument path builds no query and does not touch the cache. The `cond` path is unchanged, so its hash and cache behaviour stay the same.
- Constraint 5, table modifications through `_update_table`: respected. `count` is read-only and adds no writes.

## Risks
- Q-01 assumption: `table.count(None)` returns the total (same as no argument). If the maintainers want `None` to raise instead, the default must become a private sentinel object, and the test for `None` must change. Reject this in review if wrong.
- Q-02 assumption: "`db.count(...)`" means `Table.count` on the default table, reached through `TinyDB.__getattr__` forwarding. If a `Database.count` method is wanted, `database.py` would need a change too.
- Q-03 assumption: the existing `count(cond)` behaviour in `tests/test_tables.py` and `tests/test_tinydb.py` is the baseline. The existing tests must still pass unchanged after the edit.