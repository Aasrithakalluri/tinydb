**Review: `!=` on missing fields (tinydb issue #1)**

The change makes `where(f) != v` return True when a top-level field is missing, which fixes the reported case. The test suite passes (239 tests, which I ran). It does not match the design for nested paths, though.

- **Nested paths don't match the design.** The design says a missing or non-mapping parent should be treated as a missing field (FR-03), and it says this comes along with the `missing_result` change. The implementation adds `and len(self._path) == 1`, so nested paths keep the old `False`. I checked:
  - `(where('profile').nickname != 'bob')({})` returns `False`.
  - `(~(where('profile').nickname == 'bob'))({})` returns `True`.
  - `(where('profile').nickname != 'bob')({'profile': 5})` returns `False`.

  So `!=` and `~(==)` still disagree for nested paths. This is the RSK-02 risk the spec flagged. The restriction is not explained in the design or the test report, and no test covers it.
- **FR-03 has no missing-path tests.** Only `test_fr_03_ac4_nested_equal_value` was added, and it checks the present-field case. FR-03-AC1 to AC3 are not tested, so the nested behaviour is untested.
- **The design assumed Q-01 was settled.** The spec lists Q-01 (P1) as open and the design says it "must be confirmed before implementation". The test report does not say it was confirmed. This is a process gap, not a code defect.
- **Test file cleanup.** `tests/test_queries.py` has a run of blank lines before `test_fr_03_ac4_nested_equal_value`. Several new tests also duplicate each other (`test_ne_missing_field` and `test_fr_01_ac1`/`ac2`).

The top-level fix is correct, but the nested-path behaviour contradicts the author's own design and leaves `!=` and `~(==)` inconsistent for nested fields. I'd request either the nested behaviour the design calls for, with FR-03 tests, or an explicit decision to scope the change to top-level fields, recorded in the design.

```json
{"verdict": "changes",
 "issue_type": "code",
 "tests_run": true,
 "findings": [
  {"file": "tinydb/queries.py", "line": 247, "problem": "missing_result is ignored for nested paths (`and len(self._path) == 1`), contrary to the design's FR-03 requirement that a missing or non-mapping parent also returns True for !=. Nested != still disagrees with ~(==).", "evidence": "(where('profile').nickname != 'bob')({}) -> False while (~(where('profile').nickname == 'bob'))({}) -> True; (where('profile').nickname != 'bob')({'profile': 5}) -> False"},
  {"file": "tests/test_queries.py", "line": 580, "problem": "No tests cover FR-03 missing or non-mapping parent cases (FR-03-AC1..AC3); only the present-field case test_fr_03_ac4 is added. The nested behaviour is therefore untested and the len==1 restriction is unverified.", "evidence": "Only test_fr_03_ac4_nested_equal_value is added for nested paths; test_report lists no missing-parent nested test"},
  {"file": "tests/test_queries.py", "line": 575, "problem": "Stray blank lines before test_fr_03_ac4_nested_equal_value, and several new tests duplicate each other (test_ne_missing_field vs test_fr_01_ac1/ac2).", "evidence": "Diff shows a run of about eight empty lines before test_fr_03_ac4; test_ne_missing_field asserts the same as test_fr_01_ac1 and ac2"},
  {"file": "design.md", "line": 0, "problem": "Design assumes Q-01 (option a) without confirmation, although the spec marks Q-01 as P1 and open; the change to existing != semantics is a behaviour change for current callers and no decision or changelog entry is recorded.", "evidence": "Spec Q-01 status open; design says 'must be confirmed before implementation'; no release-note change in diff"}
 ],
 "notes": ["Top-level behaviour fix works: (where('nickname') != 'bob')({}) -> True and the full suite passes (239 passed).", "The len(self._path)==1 restriction is not documented in the design or test report; either implement FR-03 as designed or record the scoping decision and update the design.", "Behaviour change for existing != callers needs a changelog entry (RSK-01)."]}
```