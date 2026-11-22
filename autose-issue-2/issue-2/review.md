

# Review round 1 (head 6accc9e5, model: reviewer)

The change fixes the issue: a second `search()` with the same query returns the stored data, however the first result was edited. I found no defect I could reproduce.

**What must be true after the change**
- Editing a document returned by `search()`, at top level or in a nested list, must not change what a later `search()` returns.
- This must hold for both the first (cache-miss) call and repeated (cache-hit) calls.
- Writes must still invalidate the cache.

**Code read**
- `tinydb/table.py:250-299`: on a miss, each matching document is deep-copied from storage. The cache stores a separate deep copy of the result list. On a hit, a deep copy of the cache is returned. So neither the caller's documents nor the cache share objects with storage or with each other.
- Cache invalidation is untouched. `_update_table` still clears the cache.

**ARCHITECTURE.md §3 constraints**
- **Constraint 4 (layering):** `table.py` only adds `import copy` from the standard library. It still uses queries only through `QueryLike` and storages only through `Storage`. Respected.
- **Constraint 5:** I did not touch query hashes. All writes still go through `_update_table`, and the insert-invalidation test passes. Respected.
- **ADR-3 wording:** "Cached documents are shared with the caller" is now out of date, and `ARCHITECTURE.md` was not updated. That is documentation only.

**Tests**
- `python -m pytest -q`: 232 passed.

**Experiments (`python -c`)**
- **Issue example on JSON storage (`TinyDB(path)`):** I mutated the name and appended to the tags, then searched again. The result was `[{'name':'a','tags':['x']}]`. Repeating the mutation on the cache-hit result also left the data unchanged, and `db.all()` matched.
- **Empty result:** `[]` is returned consistently on repeat, so the cache check `is not None` works with empty lists.
- **`MemoryStorage`:** mutating a nested list in a result did not change `all()` or later searches. After `update()` the new value appeared, and mutating that result again did not leak.
- **Uncacheable query (`Query().t.test(lambda ...)`):** the nested mutation did not reach storage or later searches.
- **`doc_id`:** it is preserved on returned documents.

**Notes**
- `Table.get()` still returns live storage objects. With `MemoryStorage` those are live dicts. The issue is only about `search()`, so I did not count this as a finding.
- The new tests named `test_fr_01_*` and `test_fr_02_*` are oddly named, but they are valid.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["Table.get() still returns live storage objects (out of the issue's scope)", "ARCHITECTURE.md ADR-3 still says cached documents are shared with the caller; this is now outdated documentation"]}
```

**Pipeline decision input:** verdict=approve, issue_type=none, tests run by reviewer=True
