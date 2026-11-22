# Test report (attempt 1)

- full suite passed: **True**
- acceptance criteria without a test: 0

## pytest output (tail)
```
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/runner/work/tinydb/tinydb
configfile: pytest.ini
plugins: anyio-4.16.0, cov-7.1.0
collected 232 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_queries.py ..................................                 [ 24%]
tests/test_storages.py ..............                                    [ 30%]
tests/test_tables.py ...............................                     [ 43%]
tests/test_tinydb.py ................................................... [ 65%]
...................................................................      [ 94%]
tests/test_utils.py ............                                         [100%]

============================= 232 passed in 0.44s ==============================

```

## Builder summary
Files changed: `tests/test_tinydb.py` only. I did not touch `tinydb/`.

- Rewrote `test_query_cache_documents_are_shared_with_cache` to assert the copy contract. The old version asserted that returned documents were the cached objects, which contradicts the design.
- Added `test_search_results_isolated_from_cache`, which mutates results on both the miss and hit paths and checks the cache and `db.all()` are unaffected.
- Added `test_fr_01_ac1_top_level_mutation_does_not_change_later_search`, `test_fr_01_ac2_nested_mutation_does_not_change_later_search` and `test_fr_02_ac1_insert_invalidates_cached_search`, one per acceptance criterion.
- Full suite: `python -m pytest -q` gives 232 passed.

Notes:
- `Table.search` in `tinydb/table.py` already deep-copies on the hit path, the miss path and the cache store, and its docstring already describes the copy contract. I did not modify it in this mode.
- The design's ADR-3 text update and the changelog entry are not in the listed files, so I did not touch them.
- The benchmark for the deep-copy cost (RSK-01) has not been run.
