## Approach
Add one factory function `multiply(field, n)` to `tinydb/operations.py`, modelled on `add` and `subtract`. It returns a transform that does `doc[field] *= n`. Errors (missing field, non-numeric value) propagate from the transform, so `Table.update` raises before it writes, and the stored data is unchanged. Tests are added to `tests/test_operations.py`, one or more per acceptance criterion FR-01-AC1..AC4. This is the smallest change that meets the criteria and follows the existing pattern.

## Files to change
- `tinydb/operations.py` :: `multiply` (new)
- `tests/test_operations.py` :: `test_fr_01_ac1_multiply_float_factor` (new)
- `tests/test_operations.py` :: `test_fr_01_ac2_factor_zero_and_one_boundary` (new)
- `tests/test_operations.py` :: `test_fr_01_ac3_non_numeric_field_raises_and_keeps_value` (new)
- `tests/test_operations.py` :: `test_fr_01_ac4_missing_field_raises_and_keeps_document` (new)

## Constraint check
- ARCHITECTURE.md section 3, rule 4 (layering): `operations.py` still imports nothing from the package; the test file imports only the public `tinydb` and `tinydb.storages` API. Pass.
- Rule 5 (query hash): unaffected; no query code changed. Pass.
- Constraint 2 (`_update_table` is the only write path): the operation runs inside `Table.update`, which is unchanged. Pass.
- No new dependencies (`pyproject.toml` unchanged). Pass.

## Risks
- Int factor on a string field repeats the string (`'ten' * 2`) instead of raising. This is Python's default and is not guarded; the test uses a float factor for the failure case. Open question Q-03.
- Float results are inexact (10 × 1.1 ≈ 11.000000000000002). Tests use `pytest.approx`.
- Name `multiply` does not shadow any builtin; `set` already shadows the builtin in this module, which is unchanged.