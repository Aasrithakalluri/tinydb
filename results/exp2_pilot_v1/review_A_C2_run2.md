Review: `multiply` in `tinydb/operations.py`

**Expected behaviour from the issue**
- `multiply(field, n)` can be imported from `tinydb.operations`.
- It takes a field name and a factor, like `add`.
- `db.update(multiply('price', 1.1), where(...))` scales only the matching documents.

**What I checked**
- `ARCHITECTURE.md` does not exist in this checkout. A Glob for `**/ARCHITECTURE*` found nothing, so I could not check the section 3 constraints against the document.
- The change only adds a pure transform function. It does not touch the query layer, query hashing or storage. Writes still go through `db.update`, so nothing bypasses `_update_table`.
- `python -m pytest -q`: 230 passed, including the two new tests.
- Issue example: the two documents with `category == 'books'` ended up with prices 11.0 and 2.75. The output was `[{'price': 11.0, ...}, {'price': 2.75, ...}]`.
- Empty table: `update(multiply('a', 2))` returned `[]` and raised no error.
- String field (an edge case I added): `multiply('price', 2)` on `'ab'` gave `'abab'`. This is Python's `*=` behaviour. `add` allows strings in the same way, so I treat it as acceptable.
- Missing field: the new test expects a `KeyError`, which matches how `add` behaves.

**Notes**
- I did not check whether `docs/` lists the other operations, and the PR changes no docs. Documentation would be a nice addition but is not required for correctness.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["ARCHITECTURE.md not present in checkout; constraints could not be verified against it, but the change is a pure operation function and touches no layering, hashing or write paths.", "multiply on a str field repeats the string, which is Python *= semantics (consistent with add on strings).", "No docs update included; optional."]}
```