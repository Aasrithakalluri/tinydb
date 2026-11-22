# Test report (single agent, attempt 1)

- full suite passed: **True**

```
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/runner/work/tinydb/tinydb
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0, cov-7.1.0
collected 235 items

tests/test_middlewares.py .........                                      [  3%]
tests/test_operations.py ..............                                  [  9%]
tests/test_ordering.py .......                                           [ 12%]
tests/test_queries.py ..................................                 [ 27%]
tests/test_storages.py ..............                                    [ 33%]
tests/test_tables.py ...............................                     [ 46%]
tests/test_tinydb.py ................................................... [ 68%]
...............................................................          [ 94%]
tests/test_utils.py ............                                         [100%]

============================= 235 passed in 0.43s ==============================

```
