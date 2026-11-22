**Review: `!=` on missing fields (tinydb issue #1)**

**Verdict: changes.** The top-level case from the issue is fixed, but the patch deliberately keeps the old behaviour for nested paths, which breaks the `!=` / `~(==)` equivalence the issue asks for and contradicts the spec's FR-03.

**What works**
- `where('nickname') != 'bob'` now returns True for `{'name': 'c'}`, matching `~(where('nickname') == 'bob')`.
- The full suite passes on this checkout: 230 tests, 0 failures.

**Problems**
1. **Nested paths still disagree with `~(==)`.** The patch returns `missing_result and len(self._path) == 1`, so the default only applies to single-segment paths. I ran it:
   - `(Query().a.b != 'x')({})` → False, but `(~(Query().a.b == 'x'))({})` → True.
   - `(Query().a.b != 'x')({'a': 5})` → False (the parent is not a mapping), so this also differs from the negated `==`.

   The spec's FR-03 requires True for both cases. The design says the default also covers nested paths, so the `len(self._path) == 1` guard goes against the design too. If that guard is intentional, it needs to be stated and the spec changed. It is not mentioned anywhere in the design or the builder summary.

2. **The test report does not match the diff.** The report says `tests/test_queries.py` gained one test per acceptance criterion (12 tests, 242 total), and that `queries.py` was not touched. The diff does neither. It changes `queries.py` and adds only `tests/test_seed_s1.py`, with two tests, and the suite collects 230 tests here. The acceptance criteria for FR-01-AC3, FR-01-AC4, FR-02 and FR-03 are therefore not covered in the PR. The nested-path behaviour in particular has no test, which is how the bug in point 1 got through.

3. **Stray file name.** `tests/test_seed_s1.py` is not a descriptive test module name. It should be folded into `tests/test_queries.py` next to `test_ne`.

4. **Q-02 (`None` rhs) is not tested.** The patch does not change `None` handling, so the top-level `!= None` case gives True, the same as `~(== None)`. That matches option (a), but no test pins it down.

**Requested changes**
- Either make nested missing or non-mapping parents return True for `!=` (per FR-03 and the design), or document the decision and update the spec.
- Add the FR-01 to FR-03 acceptance tests to `tests/test_queries.py`, including the nested cases.
- Correct the test report so it matches the diff.

```json
{"verdict": "changes",
 "issue_type": "code",
 "tests_run": true,
 "findings": [
  {"file": "tinydb/queries.py", "line": 245, "problem": "The missing-path result is limited to single-segment paths via `len(self._path) == 1`. Nested paths with a missing or non-mapping parent still return False for `!=`, while `~(==)` returns True. This breaks the equivalence the issue asks for and FR-03.", "evidence": "(Query().a.b != 'x')({}) -> False; (~(Query().a.b == 'x'))({}) -> True; (Query().a.b != 'x')({'a': 5}) -> False"},
  {"file": "tests/test_seed_s1.py", "line": 1, "problem": "Only two top-level tests are added. No tests cover FR-01-AC3/AC4, FR-02, or any FR-03 nested-path case. The test file name is not descriptive and should sit in tests/test_queries.py.", "evidence": "Diff adds only tests/test_seed_s1.py with 2 tests; suite collects 230 tests, not the 242 the report claims"},
  {"file": "test_report.md", "line": 1, "problem": "The report says 12 criterion tests were added to tests/test_queries.py and that queries.py was not touched. The diff shows the opposite: queries.py is changed and test_queries.py is not.", "evidence": "Diff touches tinydb/queries.py and tests/test_seed_s1.py only; pytest collects 230 tests"}
 ],
 "notes": [
  "The issue's top-level example is fixed: (Query().nickname != 'bob')({'name': 'c'}) is True, matching the negated ==.",
  "The spec still lists Q-01 (behaviour change) as unresolved. The patch assumes option (a), which the issue requests, and the design says this must be confirmed before merging.",
  "None handling (Q-02) is unchanged and matches negated == for top-level fields; no test pins this down.",
  "Existing callers that rely on != excluding documents without the field will see different results, so a changelog entry is needed (RSK-01)."
 ]}
```