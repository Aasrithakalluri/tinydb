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

============================= 238 passed in 0.40s ==============================

```

## Builder summary
Summary (TEST mode):

- **Files changed:** `tests/test_queries.py` only. No changes under `tinydb/`.
- **Added tests:** one per acceptance criterion, named `test_fr_01_ac1_…` through `test_fr_03_ac3_…` (10 tests). They cover the search over the three-document table, the absent-key and non-mapping cases, the `~(== )` equivalence checks, and the present-field cases (including `None` and a list value).
- **Results:** `python -m pytest -q` reports 238 passed, 0 failed. The existing `test_ne` is unchanged and still passes.
- **Implementation:** the tests passed against the existing `tinydb/queries.py`, which already has the `default` parameter on `_generate_test` and `__ne__` passing `True`. So no fix was needed.
- **Unsure:**
  - I used the criterion-based names from the task, not the `test_ne_missing_field` / `test_ne_equals_not_eq` names listed in design.md. The criterion IDs were required.
  - I did not add a separate test for the `None`-vs-absent distinction beyond FR-03-AC2, since the criteria already cover it.
  - Behaviour is the assumed reading (Q-01 option a, Q-02 option a). Per design.md, reviewers should confirm this before merge.
