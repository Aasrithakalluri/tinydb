# Phase 3 tests with real runs

| Property | How it was tested | Result | Evidence |
|---|---|---|---|
| Trigger filtering | Creating an issue with another label started a run | Run was **skipped** (only `autose` starts the job) | run [45005041378](https://github.com/Aasrithakalluri/tinydb/actions/runs/45005041378) |
| Authorization | Real GitHub permissions API for an outsider (`octocat`, read) and the owner; 9 unit tests | Outsider refused, owner allowed (checked locally, not inside Actions) | `workflow/tests/test_policy_and_rules.py` |
| Concurrency | Second `/autose` sent while a run on the same issue was `in_progress` | Second run stayed **pending** until the first finished; no race | runs [45004040980](https://github.com/Aasrithakalluri/tinydb/actions/runs/45004040980), [45004109064](https://github.com/Aasrithakalluri/tinydb/actions/runs/45004109064) |
| Budget cap | Repo variable `AUTOSE_RUN_BUDGET_USD=0.02`, issue #30 | Pipeline reached stage 5 at **$0.016**, then refused to start the reviewer ($0.004 left) and stopped with FAILED at REVIEW and a written reason. **Gap found:** the PR (#32) stayed open with green CI and no sign it was unreviewed. Fixed: the orchestrator now comments on the PR when a run stops early. | run [45005099508](https://github.com/Aasrithakalluri/tinydb/actions/runs/45005099508) |
| Test-failure back-edge | **Fault injected** (`AUTOSE_INJECT=tests_fail_once`: the first test run is reported as failing; the failure is simulated and labelled as such in the log), issue #30 | TEST → IMPLEMENT (fix mode) → TEST → RELEASE → REVIEW, finished DONE, $0.082. **Observation:** after a failure that did not exist, the Builder grew the diff from 18 to 201 lines, "fixing" a non-problem. The scope check still passed and the reviewer approved. | run [45005429040](https://github.com/Aasrithakalluri/tinydb/actions/runs/45005429040), `fault-injected-issue30/` |
| Prompt injection | See `experiment/security/results.md` | Resisted at every stage | `results/security/injection-issue28/` |
| Review back-edge (reviewer says "changes") | **Not yet exercised.** Will be exercised by the seeded PRs in Phase 4. | – | – |
| Redesign back-edge, job timeout | **Not yet exercised.** | – | – |

Issues #28 and #30 are **extra** test issues (labels `security-test`, `pipeline-test`), not part of the five experiment issues, and are excluded from pass-rate statistics.
