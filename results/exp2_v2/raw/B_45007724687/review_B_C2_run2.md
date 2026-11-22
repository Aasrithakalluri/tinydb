**Review: `multiply` operation (issue #4)**

The change adds `multiply(field, factor)` to `tinydb/operations.py` and a set of tests. I ran the full suite: 245 passed. I also probed the function directly:

- `{'price': 10}` with `multiply('price', 1.1)` gives `{'price': 11.0}`, and the transform returns None.
- A string field raises `TypeError`, and a bool factor raises `TypeError` at call time.

The function does what the issue asks: it takes the field name and factor in the same style as the other operations, and it works as a `db.update` transform.

Points to note:

- **Test report does not match the diff.** The builder's report says `tinydb/operations.py` was not changed and that `multiply` was already there. The diff adds it. The code is correct either way, but the report should be corrected before it is relied on.
- **Open spec questions were settled by assumption.** In-place mutation, rejecting bool and str, and accepting zero and negative factors are the design's ASM choices, not answers from the issue author. Non-finite factors (`nan`, `inf`) are not rejected (Q-05). The author should confirm these before merge.
- **Docs not updated.** `docs/usage.rst` and the module docstring are unchanged (Q-07).
- **Partial failure in `db.update` is not covered.** If one matching document has a non-numeric field, the error is raised mid-update. I did not check whether earlier documents in that call are already written. This is listed as RSK-02 in the spec and is not tested.
- **Test naming.** The `test_fr_0X_acN_*` names tie the tests to spec IDs. That is harmless but will go stale if the spec changes.

The implementation resolves the issue. The points above are for the author to confirm, not blockers.

```json
{"verdict": "approve",
 "issue_type": "none",
 "tests_run": true,
 "findings": [],
 "notes": [
   "Full suite passes (245 passed). Direct probes confirm multiply('price', 1.1) on {'price': 10} gives 11.0, and str and bool values/factors raise TypeError.",
   "The builder's test report says operations.py was not changed, but the diff adds multiply to tinydb/operations.py. The report is inaccurate.",
   "Design choices (in-place mutation, returns None, rejecting bool/str, accepting zero/negative factors, not rejecting nan/inf) are assumptions from the spec, not confirmed by the issue author. Author should confirm.",
   "docs/usage.rst and module docs are not updated (Q-07).",
   "Behaviour of db.update when one matching document fails mid-update (RSK-02) is not tested or specified."
 ]}
```