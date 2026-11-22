## Approach
Add a `multiply(field, factor)` factory to `tinydb/operations.py`, written in the same closure style as `add`, `subtract` and `increment`. It returns a `transform(doc)` that mutates the matched document in place, so `Table.update` and `_update_table` need no changes. Missing fields raise `KeyError` through the plain `doc[field]` lookup, as the siblings do (ASM-01). Non-numeric values raise `TypeError` through an explicit check that runs before the multiplication, so an integer factor cannot repeat a string (ASM-02). The factor is accepted as `int` or `float` (ASM-03). Tests cover the FR-01 to FR-03 criteria and use `pytest.approx` for float results. Per the assumptions, the design proceeds with the assumed behaviour for Q-01 to Q-04.

## Files to change
- `tinydb/operations.py` :: `multiply` (new)
- `tests/test_operations.py` :: `test_multiply` (new)
- `tests/test_operations.py` :: `test_multiply_missing_field` (new)
- `tests/test_operations.py` :: `test_multiply_non_numeric_field` (new)

## Constraint check
- Constraint 1 (storages subclass `Storage`): Not affected, since no storage code is touched.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): Not affected, since `_update_table` is unchanged.
- Constraint 3 (middlewares): Not affected, since no middleware code is touched.
- Constraint 4 (layering): Respected. `operations.py` keeps importing nothing from the package, and `table.py` and `queries.py` are unchanged.
- Constraint 5 (query hashes and `_update_table`): Respected. No query is added or changed, and the update still goes through `Table.update` → `_update_table`, which clears the cache after the write.

## Risks
- Assumed behaviour, to be rejected in the PR if wrong: missing field raises `KeyError` (ASM-01), non-numeric value raises `TypeError` and is left unchanged (ASM-02), and the factor is `int` or `float` only (ASM-03). Under Q-01 or Q-02 the chosen behaviour may change to skip, which would supersede FR-02 or FR-03 and change the tests.
- Partial updates (RSK-03): `_update_table` writes only after the updater returns, so an exception during the loop skips `storage.write()` and the stored data stays unchanged for file-based storage. The in-place mutation of `table[doc_id]` may still leak into the in-memory state of `MemoryStorage` if its `read()` returns the same dict object. This was not verified in `tinydb/storages.py` and needs checking before implementation.
- Float rounding (RSK-01, Q-04): results such as 10 × 1.1 are not exact. The tests use `pytest.approx`, and the function does not round.