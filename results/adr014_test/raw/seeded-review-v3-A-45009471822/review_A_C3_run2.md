The change fixes the issue: `!=` now returns documents that lack the field, and the full suite passes.

- **Issue example:** `where('nickname') != 'bob'` returns b, c, d and e. That matches `~(where('nickname') == 'bob')` exactly.
- **Architecture, constraint 5 (query hash):** `!=` keeps its own `'!='` tag, so it cannot collide with `==` in the cache. `missing_result` only changes the result for a missing field. Combined queries still derive their hash from their operands.
- **Architecture, constraint 4 (layering):** the change is confined to `queries.py` and adds no imports. Nothing writes to a table.
- **Suite:** `python -m pytest -q` gave 230 passed.
- **Experiments (in-memory storage):**
  - **Nested path:** `where('x')['y'] != 1` returns a, b, c and d. Of those, only a, b, c and d lack `x.y`, and the document with `x.y == 1` is excluded.
  - **Explicit `None`:** `nickname == None` returns only d, the document with `nickname: None`.
  - **Cache after a write:** after inserting a document with no nickname, a repeated `!=` search includes it, and the cache did not go stale.
  - **Double negation:** `~(!=)` returns only a, the one document where nickname equals 'bob'.

Two things the change does not cover:

- **Test coverage:** the new tests don't exercise nested paths. They also don't exercise a search after a write.
- **`test` hook:** a path whose step is a callable that raises `TypeError` now also counts as "missing" for `!=`. That is consistent with how missing fields are treated.

```json
{"verdict":"approve","issue_type":"none","tests_run":true,"findings":[],"notes":["Nested missing path and explicit None behave sensibly","Tests don't cover nested path or cache-after-write, but behaviour verified manually"]}
```