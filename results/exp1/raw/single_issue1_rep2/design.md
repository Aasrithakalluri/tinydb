## Approach
Make `Query.__ne__` return the negation of the existing equality query, `~(self == rhs)`. `QueryInstance.__invert__` already turns a missing-field result (`==` returns False when the path cannot be resolved) into True. For fields that exist, `not (value == rhs)` equals `value != rhs` for ordinary values, so FR-01 holds.

The hash changes from `('!=', path, frozen rhs)` to `('not', ('==', path, frozen rhs))`, which is derived from the operand as ARCHITECTURE.md constraint 5 requires. The cache therefore keeps `!=` and `==` results apart (FR-02). The `Query` builder and `_generate_test` are unchanged. The only edit is the method body and its docstring.

## Files to change
- `tinydb/queries.py` :: `Query.__ne__`
- `tests/test_queries.py` :: `test_fr_01_ac1_missing_field_not_equal` (new)
- `tests/test_queries.py` :: `test_fr_01_ac2_missing_nested_field_not_equal` (new)
- `tests/test_queries.py` :: `test_fr_01_ac3_present_field_equal_not_matched` (new)
- `tests/test_queries.py` :: `test_fr_01_ac4_search_returns_missing_fields` (new)
- `tests/test_queries.py` :: `test_fr_02_ac1_ne_matches_negated_eq_for_missing_field` (new)
- `tests/test_queries.py` :: `test_fr_02_ac2_ne_cache_not_shared_with_eq` (new)

## Constraint check
- Layering (CON-01): `queries.py` still imports only `utils`. No new imports.
- Hash rule (CON-02): the hash is built by the existing `__invert__` from the operand's hash. It identifies the same set of documents as the query.
- Table modifications: `Table._update_table` is not touched.
- No new dependencies.
- Full suite: `python -m pytest -q` gives 234 passed (228 before, plus 6 new tests).
- Branch: git is not permitted in this session, so no branch or commit was created. The change is in the working tree.

## Risks
- RSK-01: Code that relied on `!=` excluding documents without the field now gets them. This is the intended change, but it is a behaviour change and should be noted in release notes.
- RSK-02: For element-wise types (e.g. numpy arrays), `not (a == b)` and `a != b` can differ. This is outside the issue's scope (ASM-01, Q-02).
- The cache key for `!=` changes. The cache is in memory only, so there is no persisted-data impact.