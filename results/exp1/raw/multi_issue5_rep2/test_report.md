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
tests/test_storages.py ..................                                [ 31%]
tests/test_tables.py ........................................            [ 47%]
tests/test_tinydb.py ................................................... [ 68%]
...............................................................          [ 95%]
tests/test_utils.py ............                                         [100%]

============================= 241 passed in 0.42s ==============================

```

## Builder summary
TEST mode is done. The full suite passes: 241 tests, including the 17 new ones.

Files changed:
- `tests/test_tables.py`: 16 tests for FR-01-AC1 to AC5 and FR-02-AC1 to AC4.
- `tests/test_storages.py`: 4 tests for FR-03-AC1 to AC4.

Each acceptance criterion has at least one test, named `test_<criterion>_<description>` as the TEST rules require. I did not use the test names listed in design.md, since those don't cover every criterion.

I did not change `tinydb/`. The `_sorted_doc_items` helper, `__iter__` and `search` were already in place, so no implementation defect showed up.

Things to be aware of:
- I could not confirm the `sort_keys=True` test fails without the helper, because I cannot run git to revert the change. It only checks that the reopened order is numeric.
- Tests use fresh in-memory or tmp-path databases, not the shared `db` fixture, so the fixture's existing documents do not affect the expected IDs.
- design.md's open risks still stand: ASM-01 (numeric ID order) is an assumption for the human reviewer to confirm.
