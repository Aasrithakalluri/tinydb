## Approach
Design for the ASSUMED reading of the spec: `!=` on a document where the queried path cannot be resolved returns `True` (the reporter's expectation, FR-01 with FR-02 applied to nested paths). The current `Query.__ne__` goes through `_generate_test`, whose `runner` returns `False` on `KeyError`/`TypeError`. The change is to let `_generate_test` take a parameter for the value returned on an unresolvable path, and have `__ne__` pass `True`. Present-field evaluation is unchanged (FR-03). Hash tag `'!='` stays the same, because the operator and path still identify the query. `==` and the other operators are untouched. Existing tests in `tests/test_queries.py` (`test_ne`) only cover present fields, so they keep passing. New tests cover absent and non-mapping paths and the `~(== )` equivalence. This is a public behaviour change; see Risks.

## Files to change
- `tinydb/queries.py` :: `Query._generate_test` (add parameter for the unresolvable-path result, default `False`)
- `tinydb/queries.py` :: `Query.__ne__` (pass `True` for unresolvable paths; update docstring)
- `tests/test_queries.py` :: `test_ne_missing_field` (new)
- `tests/test_queries.py` :: `test_ne_equals_not_eq` (new)
- `tests/test_queries.py` :: `test_ne` (existing, unchanged, re-run for present-field non-regression)

## Constraint check
- **Constraint 4 (layering):** Respected. The change stays inside `queries.py`, which imports only `utils`. Nothing new is imported.
- **Constraint 5 (hash identifies what it matches):** Respected. `__ne__` keeps the hash `('!=', path, freeze(rhs))`. The new semantics apply to every `!=` query alike, so the hash still determines the result. Cached results from before the change are not an issue because the cache is in memory and is per-table. I considered adding a new tag for the new semantics, but that would only be needed if old and new semantics could coexist for the same hash, and they cannot.
- **Constraint 5 (table writes through `_update_table`):** Not affected. No table code changes.
- **Constraints 1–3 (storages, middlewares):** Not affected. No storage or middleware code changes.

## Risks
- The public behaviour of `!=` changes: existing queries that relied on `!=` excluding documents without the field will return different results (RSK-01). The maintainers have not decided Q-02. This design assumes option (a). The reviewer should reject this PR if option (b) is chosen.
- The same change also covers non-mapping intermediates such as `{'profile': 5}` for `where('profile')['nick'] != 'bob'` (Q-01, option a, assumed). This is wider than the reported case. Drop it if Q-01 resolves to option (b).
- "Missing field" is taken to mean an absent key only (ASM-02). A `None` value is still a present value, so `{'nickname': None} != 'bob'` stays `True`, as before.