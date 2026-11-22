## Approach
`Query.__ne__` currently calls `_generate_test`, whose `runner()` returns `False` for a missing key before the test runs. Under the assumed interpretation (ASM-01), `!=` becomes the logical negation of `==` for the same path and value. The change is to build `__ne__` as `~(self == rhs)`, so `!=` and `~(==)` share one code path and cannot diverge. For Q-02 the design uses option (a): a non-dict intermediate is treated like a missing key and returns `True`, which is what `~(==)` already does. Only `queries.py` changes, plus a regression test. `==`, `~`, and the table layer are untouched. The hash changes from `('!=', path, value)` to the `('not', ('==', path, value))` form built by `__invert__`, which is derived from the operand and stays exact. Q-01 is answered by the ASSUMED behaviour change; it is recorded as a risk for maintainer rejection.

## Files to change
- `tinydb/queries.py` :: `Query.__ne__`
- `tests/test_queries.py` :: `test_ne_missing_field` (new)
- `tests/test_queries.py` :: `test_ne_equals_not_eq` (new)

## Constraint check
- Constraint 4 (layering): respected. `queries.py` gains no imports and still imports only `utils`; no change to `table.py` or `database.py`.
- Constraint 5 (hash identifies exactly what it matches): respected. The new `!=` hash is built from the `==` hash through `__invert__`, the same derivation used for `~`, so it encodes the operator tag, path and frozen value. The old `'!='` tag is removed, so no two different predicates share a hash.
- Constraint 5 (table modifications via `_update_table`): not affected. No table write path is touched, and no new cache-clearing logic is needed.
- Constraint 1 (storages): not affected; no storage code changes.
- Constraint 2 (storage read/write contract): not affected.
- Constraint 3 (middlewares): not affected.

## Risks
- Q-01 (ASSUMED, needs maintainer sign-off in the PR): this is a behaviour change. Existing user code that relies on `!=` excluding documents with a missing field will return different results. Any existing test asserting the old `!=` result on a missing key must be updated, and the release notes should say so.
- Q-02 (ASSUMED option a): a nested path through a non-dict intermediate (for example `where('profile').nickname` with `profile` a string) now returns `True` for `!=`. This matches `~(==)` but differs from the current `!=` result. If maintainers choose option (b), `__ne__` must special-case `TypeError` separately, which breaks the one-line negation design.
- Q-03 (ASSUMED ASM-02): a field present with value `None` still satisfies `None != 'bob'` → `True`. This is unchanged by the design, but the glossary decision on "has the field" is recorded as an assumption and needs confirmation.