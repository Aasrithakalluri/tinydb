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
collected 264 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  8%]
tests/test_queries.py ..................................                 [ 21%]
tests/test_storages.py ..............                                    [ 26%]
tests/test_tables.py .........................................           [ 42%]
tests/test_tinydb.py ................................................... [ 61%]
..................................................................       [ 86%]
tests/test_utils.py ............                                         [ 91%]
workflow/tests/test_checks.py .....                                      [ 93%]
workflow/tests/test_policy_and_rules.py ..................               [100%]

============================= 264 passed in 1.33s ==============================

```

## Builder summary
I added tests for all 13 acceptance criteria (FR-01 to FR-04). The full suite passes: 264 tests, no failures.

Files changed (tests only; `tinydb/` was not touched):
- `tests/test_tables.py`: `test_fr_01_ac1` to `ac4`, `test_fr_02_ac1` to `ac3`, `test_fr_03_ac1` to `ac3`. Also added imports for `TinyDB`, `MemoryStorage` and `Document`.
- `tests/test_tinydb.py`: `test_fr_04_ac1` to `ac3`, using JSON files in `tmp_path`.

Notes:
- The implementation already sorts by `doc_id` in `Table.__iter__` and `Table.search`, so the new tests pass without code changes. Since the tests pass on the existing code, they confirm the behaviour but don't prove the sort fixes the reported bug (design RSK-01).
- I named the tests after the criteria as specified, but they live in the existing test files, not in the `design.md` names (`test_all_returns_ascending_doc_id` and similar). I kept the criterion-based names because the TEST mode rules require them.
- The `design.md` tests for the reported behaviour are not written under those exact names. Their coverage is the same as the criteria.
- Open questions from the design still apply: ASM-02 (search order matches `all()`) and Q-04 (per-call sort cost). The pull request should note both.
- I could not run `cd` or pipe output in shell commands, so I ran pytest from the working directory without `tail`.
