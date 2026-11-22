**Review: `!=` now matches documents that lack the field. Approve.**

**Expected behaviour from the issue**
- `where('nickname') != 'bob'` should return documents that have no `nickname`.
- It should give the same result as `~(where('nickname') == 'bob')`.
- Cached results must not be mixed up between `!=` and `==` queries.

**What I checked**
- **The change.** `_generate_test` in `tinydb/queries.py:218-253` gets a `missing_result` parameter. The path-resolution failure branch returns it. Only `__ne__` passes `True`, so every other operator still returns `False` for a missing field.
- **Architecture constraints.**
  - Constraint 4 (layering): the change touches only `queries.py` and adds no imports.
  - Constraint 5 (hash must identify what the query matches): `!=` already had its own tag, `('!=', path, freeze(rhs))`, so it cannot collide with `==`. The cache check in the new test and my repeated-search experiment both confirm this.
  - Constraint 5 (writes): no write paths are touched.
- **Test suite.** `python -m pytest -q` gave 230 passed.
- **Experiments.** I ran the issue's example on `MemoryStorage`:
  - `!= 'bob'` returned b and c. `~(== 'bob')` returned the same.
  - After inserting another document without the field, a repeated `!=` search returned b, c and d, so the cache was cleared by the write.
  - A nested path (`where('x')['y'] != 1`) over documents where `x` is missing, an int, or a dict returned a, b, c, d, e. `~(where('x')['y'] == 1)` returned the same set.
  - An empty table returned `[]`.

I did not run an experiment on JSON-backed storage.

**Notes**
- The new tests are in `tests/test_seed_c3.py`. They cover a missing field and cached `!=` versus `==` on a table where every document has the field. They do not cover a missing field inside a cached query, nested paths, or the equivalence with `~`. My ad hoc runs covered those and passed.
- The changed behaviour is not documented. This is minor, so I did not raise it as a finding.

```json
{"verdict":"approve","issue_type":"none","tests_run":true,"findings":[],"notes":["Full suite: 230 passed.","Issue example, nested path, repeated cached search after a write, and empty table all behave consistently with ~(==).","New tests are thin: they don't cover nested paths, a missing field in a cached query, or equivalence with ~(==).","No JSON-backed storage experiment was run."]}
```