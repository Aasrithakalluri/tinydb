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
collected 238 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_queries.py ............................................       [ 28%]
tests/test_storages.py ..............                                    [ 34%]
tests/test_tables.py ...............................                     [ 47%]
tests/test_tinydb.py ................................................... [ 68%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

============================= 238 passed in 0.41s ==============================

```

## Builder summary
Files changed: `tests/test_queries.py` only. I appended one test per acceptance criterion, FR-01-AC1 to FR-03-AC3 (10 tests), named `test_<criterion>_<description>` as the TEST mode requires. I did not touch `tinydb/`.

Full suite: `python -m pytest -q` gives 238 passed.

- `tinydb/queries.py` already has `__ne__` returning `~(self == rhs)`, so the new tests pass against the current code. I did not verify that the pre-change behaviour would fail them.
- One test needed correction. FR-02-AC3's wording is garbled. My first draft asserted `~(==)` is `True` on `{'value': [0, 1]}`, but `==` matches there, so `~(==)` is `False`. The test now asserts that `!=` and `~(==)` both return `False`, which is the invariant the criterion is after.
- The design lists two extra test names (`test_ne_missing_field`, `test_ne_equals_not_eq`) that I did not add. The criterion-named tests cover the same behaviour.
- The FR-02-AC2 test asserts `True` for both sides, which follows the design's Q-02 option (a). If maintainers pick option (b), that assertion changes.
- FR-01-AC4 (`None` value) and the Q-01 behaviour change are asserted as the design states. The Q-01 sign-off is still needed in the PR.
