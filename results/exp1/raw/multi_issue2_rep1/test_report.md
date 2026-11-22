# Test report (attempt 1)

- full suite passed: **True**
- acceptance criteria without a test: 0

## pytest output (tail)
```
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/runner/work/tinydb/tinydb
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0, cov-7.1.0
collected 241 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_queries.py ..................................                 [ 23%]
tests/test_storages.py ..............                                    [ 29%]
tests/test_tables.py ...............................                     [ 42%]
tests/test_tinydb.py ................................................... [ 63%]
........................................................................ [ 93%]
....                                                                     [ 95%]
tests/test_utils.py ............                                         [100%]

============================= 241 passed in 0.44s ==============================

```

## Builder summary
I added tests for every acceptance criterion and for the three new tests in the design. The full suite passes (241 tests). I changed no code under `tinydb/`, because `Table.search` already returns and caches deep copies.

Files changed:
- `tests/test_tinydb.py`:
  - Rewrote `test_query_cache_documents_are_shared_with_cache` to assert isolation instead of sharing.
  - Added `test_search_miss_result_mutation_is_isolated`, `test_search_hit_result_mutation_is_isolated` and `test_search_mutation_does_not_change_storage`.
  - Added one test per criterion: `test_fr_01_ac1` through `test_fr_01_ac4`, `test_fr_02_ac1` through `test_fr_02_ac3`, and `test_fr_03_ac1` through `test_fr_03_ac3`.
  - Added `import json` to the test module header.

Things to be aware of:
- The design's assumed contract (deep copies, option a) is the one tested. A human should still confirm it, since the design marks it as assumed.
- The design lists `test_search_miss_result_mutation_is_isolated` and the other two new tests as separate from the criterion tests, so some checks overlap. I kept both sets rather than merge them.
- The `MemoryStorage` shared-object question from the design is covered only indirectly, by the miss-path test on `MemoryStorage`. It does not inspect whether storage shares objects.
- I did not measure the performance cost of the deep copies (RSK-01), which the design says should happen before merge.
