## Approach
Add one new transform factory, `multiply(field, factor)`, to `tinydb/operations.py`, following the same shape as `subtract` and `increment`. The returned transform multiplies `doc[field]` in place and returns None (ASM-01). Factor validation runs when `multiply(...)` is called, so a bad factor fails early (Q-06 eager, ASM-02). Bools and strings are rejected, because Python's `str * int` would otherwise repeat the string silently (ASM-02, ASM-03). A missing field raises `KeyError` from the normal dict lookup, before any write. `db.update` and `table.py` stay unchanged: `Table.update` already accepts any transform and routes writes through `_update_table`. Tests go in the existing `tests/test_operations.py`.

## Files to change
- `tinydb/operations.py` :: `multiply` (new)
- `tests/test_operations.py` :: `test_multiply_numeric` (new)
- `tests/test_operations.py` :: `test_multiply_boundary_factors` (new)
- `tests/test_operations.py` :: `test_multiply_rejects_non_numeric` (new)
- `tests/test_operations.py` :: `test_multiply_with_update_matches_only_query` (new)

## Constraint check
- Layering (constraint 4): respected. `operations.py` still imports only from `collections.abc` and `typing`, and nothing from the package.
- Table modifications through `_update_table` (constraint 5): respected. The change adds no write path. `db.update(multiply(...), query)` uses the existing `Table.update`, which goes through `_update_table` and clears the cache.
- Query hash identity (constraint 5): respected. No query, hash or `freeze` code is touched, and `multiply` is a transform, not a query.
- Storage rules (constraints 1–3): not affected. No storage or middleware code changes.

## Risks
- ASM-01 (in-place mutation, returns None) and ASM-02 (int/float factor only, bools and strings rejected) are assumptions taken from the spec, not answers to Q-03/Q-04/Q-06. A human should reject them in the PR if the author wants different behaviour.
- Float results such as `10 * 1.1 = 11.000000000000002` are not exact (RSK-01). The tests use a tolerance of 1e-9 (ASM-05), and no rounding is added.
- Zero and negative factors are accepted (ASM-04, Q-04). Non-finite factors such as `nan` and `inf` are not rejected in this change (Q-05), so they will pass through as float results.