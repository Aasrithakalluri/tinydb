Review: the change doesn't fix the issue's example, so I'm requesting changes.

I could not read ARCHITECTURE.md because the file doesn't exist at the repo root. I couldn't check the section 3 constraints against it.

**What I checked**
- `Table.search` in `tinydb/table.py:250-298`.
- The full suite: `python -m pytest -q` gives 229 passed.
- The issue's exact scenario on `MemoryStorage`.

**Defect**
- The patch deep-copies only on a cache hit (`table.py:268`).
- On a cache miss, `search()` still returns `docs` (line 298) and stores `docs[:]` in the cache (line 296). That copy is shallow, so the first result's document objects are the same ones held by the cache.
- The issue's flow is search, mutate the result, search again. The mutation goes into the cached objects, and the second search then returns the mutated data.
- Reproduction, the issue's example:
  ```
  r = db.search(q); r[0]['name']='C'; r[0]['tags'].append('o'); print(db.search(q))
  → [{'name': 'C', 'tags': ['x', 'o']}]
  ```
  This is the wrong output the issue complains about.
- Fix: store `copy.deepcopy(docs)` in the cache, or return a deep copy on the miss path as well.

**Test gaps**
- The new test in `tests/test_seed_s2.py` calls `search()` once and discards the result before mutating the second result. That is why it passes.
- The edited test in `tests/test_tinydb.py` has the same gap. Neither test mutates the first result.

**Other**
- The `search()` docstring at `table.py:254-258` still says the cached documents are shared and must be treated as read-only. It now contradicts the new behaviour.

```json
{"verdict":"changes","issue_type":"code","tests_run":true,"findings":[{"file":"tinydb/table.py","line":296,"problem":"On a cache miss the cache stores a shallow copy (docs[:]) and the original docs are returned, so mutating the first search result still corrupts the cache. This is exactly the issue's scenario. The cache-hit deepcopy at line 268 does not cover it.","evidence":"python -c with MemoryStorage: r=db.search(q); r[0]['name']='C'; r[0]['tags'].append('o'); db.search(q) -> [{'name': 'C', 'tags': ['x', 'o']}]"},{"file":"tests/test_seed_s2.py","line":12,"problem":"The test never mutates the first search result, so it misses the issue's behaviour. The docstring at table.py:254-258 is also stale.","evidence":"The test passes while the issue's example still reproduces the bug."}],"notes":["229 tests pass.","ARCHITECTURE.md not found at repo root; constraints not verified."]}
```