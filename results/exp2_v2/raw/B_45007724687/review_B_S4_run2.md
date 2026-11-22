**Review: `multiply` operation (issue #4)**

The operation works for the main cases. Numeric fields are multiplied, `db.update(multiply(...), query)` only touches matching documents, and bool and string values or factors are rejected. The full suite passes (244 tests; the author's report says 239, a count discrepancy but not a failure).

The blocking problem is the missing-field path. The transform does `if field not in doc: return`, so a document without the field is silently skipped. Both the author's spec (FR-03-AC1) and design say a missing field should raise `KeyError` and leave the document unchanged. I confirmed the code does not do this: applying `multiply('price', 1.1)` to `{'name': 'x'}` leaves the document untouched and raises nothing. The design's claim that "a missing field raises KeyError from the normal dict lookup" does not match the code. There is also no test for this case.

Silent skipping matters here. A typo in the field name in a bulk `db.update` would quietly update nothing and report success. The existing `add`/`subtract`/`increment` operations do not behave this way, so the new operation is also inconsistent with its siblings.

Smaller points:
- The test file has a run of four blank lines before `test_fr_03_ac2`. This is a style nit.
- The docstring does not mention the missing-field behaviour, so users cannot tell it is a silent no-op.
- `nan` and `inf` factors are accepted. The spec lists this as open question Q-05, so I am not blocking on it.

Requested change: remove the `if field not in doc: return` early exit so the `doc[field]` lookup raises `KeyError`, and add a test for FR-03-AC1 (missing field raises `KeyError` and the document is unchanged).

```json
{"verdict": "changes",
 "issue_type": "code",
 "tests_run": true,
 "findings": [
  {"file": "tinydb/operations.py", "line": 63, "problem": "A missing field is silently skipped instead of raising KeyError, contrary to the spec (FR-03-AC1) and the design. A typo in a field name in a bulk db.update silently does nothing and reports success.", "evidence": "Code: `if field not in doc: return`. Running multiply('price', 1.1)({'name': 'x'}) leaves the document unchanged with no exception."},
  {"file": "tests/test_operations.py", "line": 0, "problem": "No test covers the missing-field failure case (FR-03-AC1), so the silent-skip behaviour is untested and unspecified in the tests.", "evidence": "Test list in the diff has FR-03-AC2, AC3 and AC4 but no AC1 test."},
  {"file": "tests/test_operations.py", "line": 0, "problem": "Four stray blank lines before test_fr_03_ac2_string_value_raises_type_error.", "evidence": "Diff shows consecutive blank lines after test_fr_02_ac3_multiple_matches_all_updated."}
 ],
 "notes": [
  "The core multiply behaviour (numeric scaling, int-stays-int, query scoping through db.update) works and the full suite passes (244 passed).",
  "The test report says 239 passed; the actual run shows 244. This is a count discrepancy only.",
  "nan and inf factors are not rejected; the spec lists this as open (Q-05), so it is not blocking.",
  "Fix: drop the early return so doc[field] raises KeyError, add the FR-03-AC1 test, and tidy the blank lines."
 ]}
```