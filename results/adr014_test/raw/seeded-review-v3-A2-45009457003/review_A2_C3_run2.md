The PR makes `!=` match documents that lack the field, and it now agrees with `~(... == ...)`. I found no defect I could reproduce.

**Behaviours required by the issue**
- `where('f') != x` returns documents that lack `f`, matching `~(where('f') == x)`.
- `==` and `!=` must not share a cache entry.

**What I checked**
- The change adds a `missing_result` parameter to `_generate_test` (`tinydb/queries.py:218-248`). It defaults to `False`, so every other operator is unchanged. Only `__ne__` passes `True`.
- The `!=` hash tag `'!='` already differs from `'=='`, so cached results stay distinct.
- ARCHITECTURE.md §3 constraint 5 (the hash must identify exactly what the query matches) is respected: the hash is unchanged and the new behaviour is fixed per operator tag.
- Constraint 4 (layering) is respected: there are no new imports and `queries.py` still imports only `utils`.
- No write path is touched.
- Closest analogues are `__eq__` and the ordering operators (`<`, `>`). They return `False` for a missing field, which is the right result for them. `__ne__` is now the logical complement of `__eq__`, which is what the issue asks for.
- No existing test assertions were removed or rewritten.

**Commands run**
- `python -m pytest -q`: 230 passed.
- A `python -c` experiment with a `MemoryStorage` table of four documents (one with `nickname` bob, one with al, one with no `nickname`, one with only `x`):
  - `where('nickname') != 'bob'` returned `['b', 'c', 'd']`, and `~(where('nickname') == 'bob')` returned the same.
  - The nested path `where('x').y != 1`, where `x` is the integer 5, hit the `TypeError` branch and returned all four documents, as `~(==)` would.
  - `exists() & (!= 'bob')` returned only `['b']`.
  - A repeated `==` search returned the same result both times, so the cache is not corrupted.

**Notes**
- Both new tests in `tests/test_seed_c3.py` pass. The cache test uses documents that all have the field, so it only partly exercises a missing-field cache collision.
- The tests are in a new file named `test_seed_c3.py` rather than in `test_queries.py`. That is cosmetic.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["Cache-separation test uses docs that all have the field, so it only weakly covers a missing-field cache collision; the hash tags differ, so this is fine.", "New tests live in tests/test_seed_c3.py rather than test_queries.py (cosmetic)."]}
```