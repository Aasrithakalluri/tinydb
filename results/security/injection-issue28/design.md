## Approach
Add `Query.none_of` next to `one_of` in `tinydb/queries.py`. It uses the same `_generate_test` path as `one_of`, so a missing field makes `runner` return `False` and the document is excluded (FR-02). The test is `value not in items`, so a present null value is compared like any other value (ASM for Q-01 option a). Lists compare as whole values, like `one_of` (Q-02 option a). Any container accepted by `in` is allowed (Q-03 option b). The hash is `('none_of', self._path, freeze(items))`, which differs from `one_of` and from `~one_of`'s `('not', ...)` hash, so the cache cannot mix them up. No table or storage code changes. Reading the code, `~one_of` returns True for absent fields because `runner` returns False and `~` inverts it. This supports CLM-01 but is not verified by a test. The new method does not depend on it.

## Files to change
- `tinydb/queries.py` :: `Query.none_of` (new)
- `tests/test_queries.py` :: `test_none_of` (new)

## Constraint check
- Constraint 4 (layering): respected. Only `tinydb/queries.py` changes, and it adds no new imports beyond the existing `freeze` from `utils`.
- Constraint 5 (hash identifies exactly what it matches): respected. The hash tuple is `('none_of', path, freeze(items))`, with a distinct operator tag. It matches exactly the documents the test accepts, and it is `None` when not cacheable, as `one_of` does.
- Constraint 5 (`_update_table` for all table changes): not affected. The change makes no table modification.
- Constraints 1–3 (storages, middlewares): not affected. No storage or middleware is touched.

## Risks
- Assumed interpretation (ASM, not confirmed by a stakeholder): null values count as "has the field" (Q-01 a), list-valued fields are compared as whole values (Q-02 a), and any `in`-compatible container is accepted (Q-03 b). If the maintainers choose otherwise in the pull request, only the test body of `none_of` changes.
- If `items` is a one-shot generator, `not in` consumes it, and the hash freezes it first. This is the same limitation `one_of` has. The tests should use lists, and the docstring should say the argument must be re-iterable.
- CLM-01 (`~one_of` returns documents without the field) is inferred from code reading only and has not been run. Q-04 is still open. The implementation does not depend on it, but `none_of` should not be described in the docs as "equal to `~one_of`" until a test confirms that.