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
plugins: cov-7.1.0, anyio-4.16.0
collected 238 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_queries.py ............................................       [ 28%]
tests/test_storages.py ..............                                    [ 34%]
tests/test_tables.py ...............................                     [ 47%]
tests/test_tinydb.py ................................................... [ 68%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

============================= 238 passed in 0.27s ==============================

```

## Builder summary
Added tests for all nine acceptance criteria (FR-01-AC1 to FR-03-AC3) and a `test_none_of` unit test, all in `tests/test_queries.py`. The full suite passes: 238 tests, with no changes to `tinydb/`.

- **Files changed:** `tests/test_queries.py` only.
- **What the tests do:** the criterion tests run `none_of` against a fresh in-memory TinyDB, and `test_none_of` checks the query's runner and its hash against `one_of`.
- **Test names:** the criterion tests use the required `test_<id>_<description>` form. The design's `test_none_of` is also included, since the design lists it.
- **Unsure:** the tests encode the assumed interpretation from the design: null/empty values count as present, list values compare as whole values, and the argument can be any `in`-compatible container. Only the list form is tested, not the generator case or list-valued fields.
- **Not covered:** CLM-01 (`~one_of` matching documents without the field) has no test, as the design expects. Q-04 remains open.
