The change makes `!=` return wrong results after a cached `==` search, so I'm requesting changes. The new `!=` query carries the same hash tuple as `==`, so the two share one query-cache entry.

**What the issue needs:** `where('nickname') != 'bob'` must also return documents that have no `nickname`, matching `~(where('nickname') == 'bob')`.

**Architecture:** constraint 5 (section 3) says a query's hash must identify exactly what it matches. The diff breaks it by changing the `!=` hash tag from `'!='` to `'=='` in `tinydb/queries.py` (`__ne__`). Constraint 4 (layering) is unaffected.

**Tests:** `python -m pytest -q` gives 230 passed. The new tests only call the query on single documents. They never go through `Table.search`, so they can't see the cache problem.

**Experiments**
- On a table with `{'n':'bob'}`, `{'n':'al'}` and `{'a':1}`, I ran `search(where('n')=='bob')` and then `search(where('n')!='bob')`. The second search returned `[{'n': 'bob'}]`, which is wrong. It should return the `al` document and the `{'a':1}` document.
- `hash(where('n')=='bob') == hash(where('n')!='bob')` and `(where('n')=='bob') == (where('n')!='bob')` are both `True`.
- On a fresh table with `bob` and `al`, `search(!= 'bob')` returned `[{'n':'al'}]`. Running `search(== 'bob')` right after returned `[{'n':'al'}]`, which is also wrong. The reverse order poisons the cache too.
- The missing-field case works when only the query call is tested: `where('a').x != 'bob'` matches `{'n':'bob'}`.

**Closest analogue:** `__eq__` and the other operators each use a distinct operator tag in their hash. `~` derives its hash from its operand as `('not', hash)`. The new `!=` reuses `==`'s tag, so it differs from every sibling.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/queries.py", "line": 278, "problem": "__ne__ now uses the hash tuple ('==', path, rhs), identical to __eq__. The two queries compare equal and share a Table query-cache key, so a cached == result is returned for != (and vice versa). This violates ARCHITECTURE.md constraint 5. The correct tag is '!='.", "evidence": "python -c: search(where('n')=='bob') then search(where('n')!='bob') on a table with bob, al, and a field-less doc returned [{'n': 'bob'}] for the != search; hash(eq)==hash(ne) and eq==ne both True."}, {"file": "tests/test_seed_s6.py", "line": 1, "problem": "The tests only call the query on single documents. They do not exercise Table.search or the cache, so they cannot detect the hash collision. No test checks that != and == have different hashes.", "evidence": "230 tests pass despite the wrong cached results."}], "notes": ["The missing_result parameter on _generate_test is a reasonable approach. Only the hash tag needs to go back to '!='.", "Nested paths use the same missing_result logic, so a missing intermediate key also matches !=. This follows the issue's negation semantics, and I did not test it beyond one case."]}
```