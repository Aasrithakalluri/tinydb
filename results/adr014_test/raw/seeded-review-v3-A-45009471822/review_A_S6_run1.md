The PR has a defect I reproduced: it gives `!=` the same query hash as `==`, so cached results are wrong.

**What the issue needs**
- `where('nickname') != 'bob'` must also return documents that have no `nickname`.
- It must still work correctly alongside `==` and with the query cache.

**What I checked**
- I read `ARCHITECTURE.md`. Constraint 5 applies: a query's hash must identify exactly what it matches. ADR-3 adds that if two different queries share a hash, the cache returns wrong results.
- The diff changes the `__ne__` hash tag from `'!='` to `'=='` (`tinydb/queries.py`, the `__ne__` method). `!=` and `==` on the same path and value therefore get the same hash, so they are equal and share a cache entry.
- `python -m pytest -q`: 230 passed. The new tests only call the query on single documents. None of them runs `search` through the cache.

**Experiments**
1. I inserted `{'n':'bob'}`, `{'n':'al'}`, `{'x':1}` and ran `search(where('n')=='bob')`, then `search(where('n')!='bob')`.
   - The first search returned `[{'n':'bob'}]`, as it should.
   - The second returned `[{'n':'bob'}]` instead of `al` and the field-less document. It was served from the cache entry left by the `==` query.
2. `hash(where('n')=='bob') == hash(where('n')!='bob')` printed `True`.
3. On a fresh table, I ran `!=` first and then `==`. Both returned `[{'n':'al'}]`, so `==` also returned the wrong result.

In the issue's own scenario, calling `==` and `!=` on one table in either order gives wrong answers. That is worse than the original bug.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/queries.py", "line": 278, "problem": "__ne__ now uses hash tag '==' instead of '!=', so != and == queries share a hash and a query-cache entry. This violates constraint 5 and ADR-3: the cache returns the other query's results.", "evidence": "python -c: after search(where('n')=='bob') -> [{'n':'bob'}], search(where('n')!='bob') also returns [{'n':'bob'}]; hash(==)==hash(!=) prints True; on a fresh table, != first then == both return [{'n':'al'}]."}], "notes": ["The missing_result=True approach is fine. Restore the '!=' hash tag.", "Add a test that runs == and != through Table.search on the same table, so the cache collision is covered."]}
```