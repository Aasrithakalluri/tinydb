The PR adds `multiply` and it works for the issue's example, but it handles a missing field differently from the other operations. I'm requesting changes.

**What I checked**
- **Issue behaviour:** `multiply('price', 1.1)` applied through `db.update` with a `where` filter updates only the matching documents. A document with `price` 10 became 11.0.
- **Architecture:** the change only touches `operations.py`, which imports nothing from the package. Writes still go through `Table.update`, which uses `_update_table`. No query hash is involved. Constraints 4 and 5 of section 3 are respected.
- **Tests:** `python -m pytest -q` gives 244 passed.
- **Experiments:**
  - A mixed table where one document has `price` and one doesn't: `multiply` skips the document without `price`. `subtract('price', 1)` on the same table raises `KeyError('price')`.
  - A `Decimal` field: `multiply` raises `TypeError`. The sibling operations accept any type that supports the operator.

**Comparison with the closest analogues** (`add`, `subtract`, `increment`, `decrement`)
- **Missing field:** the siblings raise `KeyError`. `multiply` returns silently (`operations.py:60-61`). The issue asks for the "same style as the other operations", so this is an unjustified difference. It also hides data problems.
- **Type handling:** the siblings do no validation. `multiply` rejects `bool`, `Decimal` and other numeric types, and raises eagerly on a non-numeric factor. This is stricter than the issue asked for and is a lesser concern.

**Test coverage**
- No test covers the missing-field case, so the silent skip is untested.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/operations.py", "line": 60, "problem": "A missing field is silently skipped. The sibling operations (add, subtract, increment, decrement) raise KeyError for a missing field, and the issue asks for the same style as them.", "evidence": "python -c: with documents {'c':'b','price':10} and {'c':'b'}, update(multiply('price',1.1)) leaves the second document untouched. update(subtract('price',1)) on the same table raises KeyError('price')."}, {"file": "tinydb/operations.py", "line": 63, "problem": "The extra type validation rejects bool, Decimal and Fraction values and factors. The siblings accept anything that supports the operator. This is a behavioural difference the issue does not request.", "evidence": "python -c: a document {'p': Decimal('2')} with multiply('p', 2) raises TypeError(\"field 'p' must be int or float, not Decimal\")."}], "notes": ["No test covers the missing-field behaviour. The tests carry FR/AC naming and an empty gap where an FR-03 AC1 test seems to be missing, so the spec for missing fields may have been dropped."]}
```