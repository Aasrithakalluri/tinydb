## Approach
Change only `Query.__ne__` so that a document whose queried path cannot be resolved (missing key, or a non-mapping parent, which both raise `KeyError`/`TypeError`) returns True instead of False. The cleanest way is to give the existing `Query._generate_test` helper an optional argument for the value returned when path resolution fails, defaulting to False so every other operator is unchanged, and have `__ne__` pass True. The `!=` hash tuple stays `('!=', path, frozen rhs)`, since it still identifies the same query; only the result for missing fields changes. This follows the issue's option (a) and matches `~(==)` for missing fields. Q-01 (P1) is still open in the spec, so this design assumes option (a) and must be confirmed before implementation. No new imports or modules are needed.

## Files to change
- `tinydb/queries.py` :: `Query._generate_test` (add optional missing-path result parameter, default False)
- `tinydb/queries.py` :: `Query.__ne__`
- `tests/test_queries.py` :: `test_ne_missing_field` (new)

## Constraint check
- Constraint 1 (storage subclassing): not affected, no storage code is touched.
- Constraint 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected, no storage or table I/O is touched.
- Constraint 3 (middlewares): not affected, no middleware code is touched.
- Constraint 4 (layering): respected. Only `queries.py` changes and it adds no imports; `table.py` and `database.py` are not involved.
- Constraint 5 (hash identifies exactly what is matched): respected with a caveat. The `!=` hash tuple is unchanged and still describes the operator, path and frozen argument, and the new semantics apply uniformly to every `!=` query. `~` still derives its hash from the `==` operand and is unaffected. The `hashval` for `!=` is no longer a complete description of the match result only if the default is varied per call, which the design avoids by fixing it to True in `__ne__`.
- ARCHITECTURE section 1 "every table change goes through `_update_table`": not applicable, since the change is read-only query evaluation.
- ADR-3 (query cache): cached `!=` results from before the change would be stale. The cache is in memory per table and is rebuilt on each process start, so no migration is needed.

## Risks
- Q-01 (and Q-02/Q-03) is unresolved. If maintainers choose option (b), the whole change is void, and the `None` and nested-path cases must match the chosen option, or the `!=`/`~(==)` equivalence in FR-01-AC4 breaks.
- Existing callers who rely on `!=` excluding documents without the field will see different results. This needs a changelog or release note.
- Nested paths: the same default also covers a non-mapping intermediate (`TypeError`), so FR-03 behaviour comes along with this change. The test set must cover both FR-03 and the `None` case (ASM-03) to avoid an unintended change.