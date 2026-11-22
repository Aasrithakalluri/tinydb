# Experiment 2, pilot (seed set v1), runs [45007013124](https://github.com/Aasrithakalluri/tinydb/actions/runs/45007013124) (A) and [45007020804](https://github.com/Aasrithakalluri/tinydb/actions/runs/45007020804) (B)

Seeds v1 were built from **my own reference fixes** plus one injected defect, while variant B was given the author's artifacts (spec, design, test report) of the **real pipeline runs**. Those artifacts described different code from the diff under review. This is a **confound**, so the pilot is kept as evidence but is not the main result (see `results/exp2_v2/`).

| | caught (changes on defective) | false approvals | false rejections (correct controls) | cost |
|---|---|---|---|---|
| A: Sonnet, independent (14 reviews) | 8/10 | 2/10 (S4 twice) | 0/4 | $0.384 |
| B: Haiku, sees author's artifacts (14 reviews) | 10/10 | 0/10 | 2/4 (C2 twice) | $0.044 |

What the reviews say (read, not only counted):
- Every one of A's 8 catches names the seeded defect. A **saw** S4's silent skip ("no error") and judged it acceptable: the issue only says "same style as the other operations", and A did not compare with the siblings that raise `KeyError`.
- B caught S4 because **the spec said a missing field must raise `KeyError`** (FR-03-AC1), i.e. it was checking against the author's requirement, not finding the bug independently. B also rejected the correct control C2 twice because the spec (from the real run) demanded type validation that my control did not implement. B's S4 run 2 led with a wrong finding (no type validation) and had the real one second.
- B noticed that the test report claimed tests that the diff did not contain, an artifact of the confound.
- Both variants saw that S2's `Table.search` docstring was stale and that `test_query_cache_documents_are_shared_with_cache` had been rewritten, but neither raised it as a design/approach problem needing a human decision (`issue_type` was `code`).
- The seeds branched from the baseline commit, which has no `ARCHITECTURE.md`, so A reported it could not check the architecture constraints on the seeded PRs.
