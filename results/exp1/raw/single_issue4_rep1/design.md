## Approach
Add one function `multiply(field, n)` to `tinydb/operations.py`, written exactly like `add` and `subtract`: a closure `transform(doc)` that does `doc[field] *= n` and returns it. It takes the field name and the factor, and it accepts int or float factors. No other module changes. Tests cover each acceptance criterion through `db.update` for the value cases and directly on a dict for the missing-field case, so the failure is raised by the transform itself.

## Files to change
- `tinydb/operations.py` :: `multiply` (new)
- `tests/test_operations.py` :: `test_fr_01_ac1_int_factor` (new)
- `tests/test_operations.py` :: `test_fr_01_ac2_float_factor` (new)
- `tests/test_operations.py` :: `test_fr_01_ac3_zero_factor` (new)
- `tests/test_operations.py` :: `test_fr_01_ac4_missing_field` (new)

## Constraint check
- CON-01 (operations imports nothing from the package): the change adds no import; `multiply` uses only the existing `Union`, `Callable`, `MutableMapping` types. PASS.
- CON-02 (writes go through `Table.update`): the operation is passed to `Table.update` as the existing operations are, and no table code changes. PASS.
- ARCHITECTURE.md section 3 rules 1–5 (storages, middlewares, layering, query hashing): not touched. PASS.

## Risks
- Non-numeric fields are not guarded. `str * int` silently repeats the string, and `float * str` raises TypeError. This matches the existing `subtract` and `increment` (no guard), and is recorded as RSK-01.
- Floating-point rounding (for example 1.1 times 10 gives 11.000000000000002). The tests use `pytest.approx`. Rounding rules are open (Q-04).
- No git branch was created, because git commands were not permitted in this session. The changes are in the working tree only.