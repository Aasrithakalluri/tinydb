## Approach
Add a new transform factory `multiply(field, factor)` to `tinydb/operations.py`, following the existing pattern: it returns a `transform(doc)` closure that does `doc[field] *= factor` and nothing else. `db.update` already accepts such transforms through `Table._update_table`, so no change to `table.py` or `queries.py` is needed. Per the working interpretation, a missing field raises `KeyError` and a non-numeric value raises `TypeError`, matching `add`/`subtract` (ASM-02, ASM-03). The factor is not validated (ASM-04). Tests are added to `tests/test_operations.py` and cover the FR-01 acceptance criteria plus the FR-02/FR-03 assumed behaviour. The change is limited to a new function, so no query hash or cache logic is affected.

## Files to change
- `tinydb/operations.py` :: `multiply` (new)
- `tests/test_operations.py` :: `test_multiply` (new)
- `tests/test_operations.py` :: `test_multiply_missing_field` (new)
- `tests/test_operations.py` :: `test_multiply_non_numeric` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): not affected, no storage code is touched.
- Constraint 2 (`read()`/`write()` whole-database contract): not affected, the change is a pure in-memory transform.
- Constraint 3 (middlewares): not affected, no middleware code is touched.
- Constraint 4 (layering): respected. `operations.py` imports nothing from the package and the change adds no imports.
- Constraint 5 (query hash identifies what it matches): respected. No query is created or changed. The transform is applied by `Table.update` through `_update_table`, which already clears the query cache after the write.
- ADR-1/ADR-3 (whole-database writes, hashable queries): not affected.
- "All table changes go through `_update_table`": respected, because `multiply` only mutates the document inside the updater that `Table.update` already passes to `_update_table`.

## Risks
- ASSUMED behaviour (ASM-02, ASM-03): a missing field raises `KeyError` and a non-numeric value raises `TypeError`, with the document left unchanged. Q-01 to Q-03 are still open, so a human should confirm or reject this in the pull request. If the issue author prefers skip or treat-as-zero, FR-02 and its test change.
- A string field multiplied by an int factor (for example `'ab' * 2`) silently repeats the string without error (RSK-01, Q-03). Rejecting `str` values explicitly is a possible follow-up, and this design does not add it unless the reviewer asks for it.
- Float results such as `10 * 1.1 = 11.000000000000002` mean tests must compare with `pytest.approx`, and stored values are floats after an update (RSK-03). Factor 0 and negative factors are accepted without validation (ASM-04, Q-06).