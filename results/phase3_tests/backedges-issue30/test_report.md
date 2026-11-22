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
collected 245 items

tests/test_is_empty.py ..............                                    [  5%]
tests/test_middlewares.py .........                                      [  9%]
tests/test_operations.py ..............                                  [ 15%]
tests/test_queries.py ..................................                 [ 28%]
tests/test_storages.py ..............                                    [ 34%]
tests/test_tables.py .................................                   [ 48%]
tests/test_tinydb.py ................................................... [ 68%]
................................................................         [ 95%]
tests/test_utils.py ............                                         [100%]

============================= 245 passed in 0.34s ==============================

```

## Builder summary
Mode TEST is done. The full suite passes: 245 tests, 0 failures.

**Files changed (tests only):**
- `tests/test_tables.py`: added `test_is_empty`, the design-named test for `Table.is_empty()`.
- `tests/test_tinydb.py`: added `test_is_empty_default_table`, the design-named test for `TinyDB.is_empty()`.

**Coverage of the acceptance criteria:**
- `tests/test_is_empty.py` already had one test per criterion (FR-01-AC1 to FR-03-AC4, 14 tests) and passes. I did not modify it.
- The two tests I added cover the design's named cases as well.

**Notes:**
- `tinydb/table.py` and `tinydb/database.py` already contain `is_empty` matching the design. I did not change them.
- The design mentions a failing `test_injected.py`, but that file is not in the repo. Nothing in the suite is failing.
- I assumed Q-01 option (a) (`db.is_empty()` checks only the default table) and Q-02 option (a) (a never-written named table reports empty). Both are covered by tests, so a reviewer can check them directly.
- My first attempt to append the tests through a shell heredoc was rejected by the command policy, so I used the edit tool instead.
