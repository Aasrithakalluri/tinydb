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
collected 248 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_queries.py ..................................                 [ 22%]
tests/test_storages.py ..............                                    [ 28%]
tests/test_tables.py ................................................... [ 49%]
                                                                         [ 49%]
tests/test_tinydb.py ................................................... [ 69%]
...............................................................          [ 95%]
tests/test_utils.py ............                                         [100%]

============================= 248 passed in 0.50s ==============================

```

## Builder summary
Mode TEST: I added tests for all ten acceptance criteria and the full suite passes (248 passed).

Files changed:
- `tests/test_tables.py`: appended 10 tests, one per criterion, named `test_fr_01_ac1_…` through `test_fr_03_ac2_…`. They use the existing parametrised `db` fixture.

Notes:
- I did not touch `tinydb/`. `Table.count` already has the `cond=None` default and the `len(self)` path that design.md describes, so the new tests passed against the existing implementation.
- FR-03 tests only cover `count(None)` returning the total, as the criteria specify. They do not settle the open question Q-01 about whether an explicit `None` should raise.
- FR-02-AC3 uses `where('id').exists()` on a table with mixed documents and expects 2, not 4. It passes.
- I ran pytest with `python -m pytest -q` from the repo root. An earlier attempt with `cd … &&` was rejected by the command allowlist, so I reran it without the `cd`.
