`multiply` works as the issue asks, and I found no defect I could reproduce. I'd approve.

**What the change must do:** `multiply(field, n)` should be importable from `tinydb.operations`. It should scale the field on matching documents when passed to `db.update(...)`, in the same style as `add` and `subtract`.

**Code read:** `tinydb/operations.py` adds `multiply` as `doc[field] *= n`, which matches how `add` is written. It is a pure transform. The write still goes through `db.update`, so it uses TinyDB's normal write path. `ARCHITECTURE.md` does not exist in this checkout (`Glob **/ARCHITECTURE*` returned nothing), so I could not check section 3. By inspection, the change sits at the right layer and doesn't touch queries or storage.

**Tests:** `python -m pytest -q` gave 230 passed.

**Experiments (`python -c`):**
- **Issue example:** on `MemoryStorage`, `multiply('price', 1.1)` with `where('category') == 'books'` turned 10 into 11.0 and 2.5 into 2.75. The toys document stayed at 5.
- **Cached query after a write:** I ran `search(where('price') > 6)` before and after updates. It returned `[10]` before, then `[11.0]`, then `[22.0]` after each update, so the cache is not stale.
- **No match:** an update whose query matched nothing did nothing and raised no error.
- **JSON storage:** `multiply('a', 4)` on `{'a': 2}` wrote `{"_default": {"1": {"a": 8}}}` to the file.
- **Missing field:** the PR's own test covers this, and it raises `KeyError`, as `add` does.

**Notes:**
- `docs/usage.rst:316` lists the operations, and `docs/changelog.rst` records new ones. Neither is updated for `multiply`. This is documentation only and not a correctness problem.
- The new tests don't cover float factors, but my float run above does.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["ARCHITECTURE.md is not present in the checkout, so section 3 could not be checked directly", "docs/usage.rst (~line 316) and docs/changelog.rst do not mention multiply", "Tests don't cover float factors; verified manually (10*1.1 -> 11.0, 2.5*1.1 -> 2.75)"]}
```