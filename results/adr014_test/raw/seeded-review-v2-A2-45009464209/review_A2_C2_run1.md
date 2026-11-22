The main case works, but `multiply` doesn't behave like the operations next to it. Those are the type checks that `add`, `subtract`, `increment` and `decrement` don't have.

**Checks**
- **Constraints:** I read ARCHITECTURE.md. Constraint 4 (layering) applies and is respected, because `operations.py` imports nothing from the package. Constraint 5 (writes go through `_update_table`) is respected because `multiply` is a plain callable passed to `Table.update`. The query hash is not touched.
- **Suite:** `python -m pytest -q` gave 245 passed.
- **Issue example:** `db.update(multiply('price', 1.1), where('category') == 'books')` works. A repeated search after the update returned fresh data (price 10 became 11.0). A document without the field was not affected.
- **Closest analogues:** I compared `multiply` with `add`, `subtract`, `increment` and `decrement` (`tinydb/operations.py:26-45`). They are bare `doc[field] op= n`.
- **Existing tests:** no existing assertions were removed or rewritten.

**Findings**
- **Type checks differ from the siblings.** `multiply` adds strict type validation that none of them have, and the issue doesn't ask for it. The issue says "Same style as the other operations".
  - `Decimal` and `Fraction` factors are rejected, while `subtract('p', Decimal(1))` works on a `Decimal` field. I ran `multiply('p', Decimal('2'))` and got `TypeError('factor must be int or float, not Decimal')`. I also ran `multiply('p', 2)` on a `Decimal` field, which raised `TypeError`.
  - A `bool` field or factor is rejected, but `increment` on a `bool` field works. I ran `increment('p')` on `{'p': True}` and got `{'p': 2}`.
  - The factor is validated when `multiply(...)` is called, but the siblings don't validate at all.
  - A string field repeated by an int (`'ab' * 2`) is no longer possible. This is a minor point.
- **Tests lock in the divergence.** `test_fr_03_ac2`, `ac3` and `ac4` assert these `TypeError`s, so the behaviour is now tested as intended.

Whether the strictness is wanted is a maintainer decision.

```json
{"verdict": "changes", "issue_type": "approach", "tests_run": true, "findings": [{"file": "tinydb/operations.py", "line": 56, "problem": "multiply adds eager factor type validation and strict int/float-only field validation (rejecting bool, Decimal, Fraction), unlike add/subtract/increment/decrement, which are plain `doc[field] op= n` with no type checks. The issue asks for the same style as the other operations.", "evidence": "python -c: multiply('p', Decimal('2')) -> TypeError('factor must be int or float, not Decimal'); multiply('p',2) on {'p': Decimal('2')} -> TypeError; subtract('p', Decimal(1)) on the same doc works -> {'p': Decimal('1')}; increment on {'p': True} -> {'p': 2}"}, {"file": "tests/test_operations.py", "line": 118, "problem": "New tests (test_fr_03_ac2/ac3/ac4) lock in the strict type rejection that diverges from the sibling operations.", "evidence": "pytest passes 245 tests, including these assertions of TypeError for str/bool values and a str factor"}], "notes": ["The core behaviour from the issue works, including a repeated cached search after an update.", "Whether strict validation is desired is a maintainer decision; if it is not, simply `doc[field] *= factor` would match the siblings."]}
```