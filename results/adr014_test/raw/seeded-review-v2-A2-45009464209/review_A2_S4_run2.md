Missing-field handling differs from the sibling operations, so I'm requesting changes.

**What I checked**
- The issue asks for `multiply(field, factor)` in `tinydb.operations`, in the same style as `add` and `subtract`.
- `ARCHITECTURE.md` section 3 constraint 4 applies: `operations.py` imports nothing from the package. The change respects it, since it adds no imports.
- Constraint 5 (writes go through `_update_table`) is not touched. The operation only mutates the document that `Table.update` passes in.
- `python -m pytest -q` gave 244 passed.
- The issue's example works. Your tests cover `multiply('price', 1.1)` on matching documents, and they pass.

**Experiment on the closest analogue**
I ran `subtract('p', 1)` and `multiply('p', 2)` through `db.update` on a document with no `p` field:
- `subtract` raised `KeyError`. `add`, `increment` and `decrement` do the same, because they all do `doc[field] op= n`.
- `multiply` raised nothing and left the document unchanged.

The issue asks for the "same style as the other operations", and the sibling operations are the convention. This difference means a typo in the field name passes silently. It also hides documents that lack the field. Nothing in the issue asks for this behaviour, and no test covers it. A test for the missing-field case is also absent.

**Other differences from the siblings**
- `multiply` rejects bool values and non-numeric values with a `TypeError`. The siblings do no type validation, and `add` explicitly supports strings. The strictness is defensible, but it is stricter than the convention. It also validates the factor at construction time, which the siblings do not do.

```json
{"verdict": "changes", "issue_type": "code", "tests_run": true, "findings": [{"file": "tinydb/operations.py", "line": 60, "problem": "multiply silently skips documents that lack the field. subtract, add, increment and decrement raise KeyError in that case. The issue asks for the same style as the other operations and does not ask for silent skipping. A typo in the field name is silently ignored, and no test covers this case.", "evidence": "python -c: db.update(subtract('p',1), where('c')==1) on a document without 'p' raises KeyError. db.update(multiply('p',2), ...) raises nothing and leaves the document unchanged."}], "notes": ["Full suite passes: 244 passed.", "The bool and string TypeError checks and the factor validation at construction are stricter than the sibling operations. A human may want to confirm that is intended.", "The tests do not include a case for a missing field."]}
```