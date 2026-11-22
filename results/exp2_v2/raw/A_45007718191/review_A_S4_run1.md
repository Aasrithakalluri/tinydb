**Review of the `multiply` operation: approve**

**Expected behaviour from the issue**
- `from tinydb.operations import multiply` works.
- `multiply(field, factor)` returns a transform that `db.update(...)` accepts.
- Only the matching documents are scaled.

**Architecture (section 3)**
- Constraint 4 (layering) is respected. `operations.py` imports nothing new from the package.
- Constraint 5 is respected. `multiply` is a plain transform that `Table.update` applies, so the write goes through `_update_table`, which clears the query cache. No query hashes are touched.

**Test suite**
`python -m pytest -q` gave 244 passed.

**Experiments**
- Issue example: three documents, with `multiply('price', 1.1)` applied where `category == 'books'`. The book with a price became `11.0`, and the toy price stayed `1`.
- Missing field: the book document without `price` was left unchanged and no error was raised.
- Nested value: `multiply('p', 2)` on a dict-valued field raised `TypeError`, and the document was not modified.
- Not run: JSON-backed storage, and a cached query repeated after a write. Both depend on `Table.update`, which the PR doesn't change.

**Notes**
- A missing field is silently skipped. The existing `add` and `subtract` raise `KeyError` in that case. Skipping is arguably friendlier, but it is inconsistent with them.
- `update()` still counts and returns the id of a document that was skipped for lacking the field.
- Rejecting `bool` and non-numeric types, such as `Decimal`, is stricter than the other operations. This is a design choice and not a defect.

```json
{"verdict": "approve", "issue_type": "none", "tests_run": true, "findings": [], "notes": ["Missing field is silently skipped, unlike add/subtract which raise KeyError; update() still reports that doc id as updated.", "Strict type checks (bool/Decimal rejected) are stricter than sibling operations.", "JSON-backed storage and repeated cached queries after a write were not run; they depend on Table.update, which the PR does not change."]}
```