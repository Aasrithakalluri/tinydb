# Pass rate per stage

Source: the orchestrator's own `state.json` of the final run of each issue (`results/final_states/`, aggregated by `results/aggregate.py` into `results.csv`). A stage "passes first try" if its deterministic check (ADR-007) did not fail and no retry was needed.

## View 1: agents' work, final run of the 5 experiment issues
| Stage | First-try pass | Notes |
|---|---|---|
| 1 Requirements (spec lint) | 5/5 | #5 has a second Planner call, but that is the revision after the maintainer's answers (ask mode), not a failed check |
| 2 Design (design lint) | 4/5 | #3: the Planner named a test symbol that did not exist; the check caught it and one retry fixed it |
| 3 Implementation (builds, scope) | 5/5 | |
| 4 Testing (suite + every acceptance criterion tested) | 5/5 | no test-failure loop was needed by a real run (the loop was exercised only by fault injection, issue #30) |
| 5 Release (PR + CI) | 5/5 | after pipeline fixes (View 2) |
| 6 Review (approval) | 5/5 | approved in round 1 each time (see `analysis.md` for what that is worth) |

All 5 final runs ended DONE. Cost of the 7 final runs including the two extra test issues: $0.534; 2.49M input / 178k output tokens.

## View 2: every attempt that ended in a failure, and whose fault it was
| # | Issue | Stage that failed | Cause | Agent or pipeline? |
|---|---|---|---|---|
| 1 | (workflow) | start | `runner` context used in job-level `env` (invalid YAML) | pipeline |
| 2 | #3 | 5 Release | repo setting "allow Actions to create PRs" was off | setup |
| 3 | #3 | 5 Release | restart restored `state.json` but not the code (empty commit) and waited on a gated CI run (ADR-011) | pipeline |
| 4 | #3 | 5 Release | restart tried to create a second PR | pipeline |
| 5 | #4 | 1 Requirements | my AC regex rejected the skill's tagged form `FR-03-AC1 (failure):` (ADR-012) | pipeline |
| 6 | #5 | 3 Implementation | the design said "do not implement until Q-01 is answered", nobody could answer (ADR-012/013) | pipeline design gap |
| 7, 8 | #5 | resume | restore picked a finished run's artifact (API lists by id, not time) | pipeline |
| 9, 10 | #5 | 5 Release | repo CI red because `pytest` collected the workflow's own tests; restart kept an old base (ADR-011 addendum 2) | pipeline |
| 11 | #30 | 6 Review | budget cap set to $0.02 on purpose | test |

**11 failed attempts, none caused by the agents' capability; 10 were pipeline or setup defects of mine, 1 was a deliberate test.** In the same period the agents' own checks caught real errors and retried (one design retry on #3, one spec retry on #30). This is the main point for "what went wrong": the hard failures were in the plumbing (state, restart, CI, restore), and the design lint and test gate did their job.

Caveat: five issues, one run each of the final version, so "first-try pass rate" has very wide uncertainty.
