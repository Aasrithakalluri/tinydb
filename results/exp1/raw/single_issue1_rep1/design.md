## Approach
`Query.__ne__` is built with `_generate_test`, whose path resolver returns `False` when a key is missing (`KeyError`/`TypeError`). That makes `!=` on an absent field return False, while `~(==)` returns True. The smallest fix is to let `_generate_test` take a `default_if_missing` flag (default `False`, so all other operators are unchanged) and have `__ne__` pass `True`. The test function itself is untouched; only the "could not resolve" result changes. The hash tuple `('!=', path, frozen(rhs))` is kept as is, because it still identifies the operator, path and argument.

## Files to change
- `tinydb/queries.py` :: `Query._generate_test` (existing; adds `default_if_missing: bool = False` parameter, returned when path resolution fails)
- `tinydb/queries.py` :: `Query.__ne__` (existing; passes `default_if_missing=True`)
- `tests/test_queries.py` :: `test_fr_01_ac1_missing_field` (new)
- `tests/test_queries.py` :: `test_fr_01_ac2_equal_value` (new)
- `tests/test_queries.py` :: `test_fr_02_ac1_nested_missing_parent` (new)

## Constraint check
- CON-01 / Layering (ARCHITECTURE.md §3 rule 4): only `tinydb/queries.py` changes; no new imports; `queries.py` still imports only `utils`.
- Hash correctness (rule 5): the `!=` hash tuple is unchanged and is a deterministic function of operator, path and frozen argument. Cached results for a given query stay consistent within a process because the cache is cleared on writes and the new semantics are the same for every call with that hash.
- Storage and middleware rules (1–3): not touched.
- Existing `test_ne` assertions still hold (documents with the field present behave as before).

## Risks
- Behaviour change for existing users: `!=` now returns documents without the field (RSK-01). Documented as a change to be noted in the changelog.
- Nested non-dict parents (FR-02) are treated as missing; this is ASSUMED (ASM-01, Q-01) and could be reversed by changing only the `default_if_missing` argument for that path case.
- `Query.map(...)` or custom callables in the path that raise `TypeError` for reasons other than a missing key will now also make `!=` return True; this is consistent with the existing "missing" handling but is a broader effect.

---
Note: the full suite passes (`python -m pytest -q`: 231 passed). I could not create a branch or commit, because git commands are not permitted in this session; the changes are in the working tree.