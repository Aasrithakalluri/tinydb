## Approach
Make `Table.count` take an optional condition (`cond: QueryLike | None = None`). When no condition is given, return `len(self)`, which is `len(self._read_table())` and counts every stored document, including ones without an `'id'` field. When a condition is given, keep the existing `len(self.search(cond))` path unchanged, so the query cache and its hash keys are not touched. Explicit `count(None)` follows the assumed interpretation (ASM-01, Q-01): it is treated like no argument. The `TinyDB` forwarding question (Q-02) is also resolved by assumption: `TinyDB.__getattr__` already forwards `count` to the default table, so the change applies there with no extra code. No storage, `_update_table` or query code changes. Read-only path, no new imports.

## Files to change
- `tinydb/table.py` :: `Table.count`
- `tests/test_tables.py` :: `test_count_without_condition` (new)
- `tests/test_tables.py` :: `test_count_none_condition` (new)
- `tests/test_tinydb.py` :: `test_count` (extend with the no-argument case on the `TinyDB` object)

## Constraint check
- Rule 1 (storage subclassing): not affected, no storage changes.
- Rule 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected. `len(self)` goes through the existing `_read_table()`, which already handles the empty case.
- Rule 3 (middlewares): not affected, no middleware changes.
- Rule 4 (layering): respected. The change stays inside `table.py`, adds no imports, and `queries.py` is not touched.
- Rule 5 (query hash identifies exactly what it matches): respected. The no-argument path does not create a query and does not use the cache. The conditional path still passes the same query object to `search`, so its hash is unchanged. Nothing in `queries.py` changes.
- "All table changes go through `_update_table`": not affected. `count` is read-only and does not write.

## Risks
- ASSUMED (ASM-01, Q-01, Q-02): `count(None)` is treated the same as `count()`, so it now returns the total instead of raising. A maintainer should reject this in the PR if they want `None` to stay an error. The tests named above lock in this choice.
- ASSUMED (ASM-01): "total" means every stored document, including those without `'id'`, which is what `len(table)` returns. If the author means only documents that have an `'id'`, the implementation must change.
- Q-03 is unresolved ("records" vs. "documents"). This has no effect on the implementation, but the PR should note it for the issue author.