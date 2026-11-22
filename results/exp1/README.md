# Experiment 1 (ADR-001): one agent vs three agents for stages 1 to 4

**Question.** Does splitting stages 1 to 4 over a Planner and a Builder (variant **multi**, the production design) beat one agent doing all four stages in one session (variant **single**, with the Builder's tools and the same instructions)?

**Method.** The same Haiku model, the same checks, the same retry budgets. Each run stops after stage 4 (no PR, no CI, no reviewer: stages 5 and 6 are identical in both variants). 5 issues x 2 modes x 2 repeats = 20 runs, run [45018696619](https://github.com/Aasrithakalluri/tinydb/actions/runs/45018696619). Scored locally: each run's `diff.patch` is applied to the run's base commit and the private hidden tests are run (`experiment/exp1/score.py`; raw artifacts in `raw/`, per-run table in `results.csv`). The extra test of issue 5 (`test_extra_...`) is reported separately, as before.

## Result
| | multi (3 agents) | single (1 agent) |
|---|---|---|
| runs completed (all checks pass) | 10/10 | 10/10 |
| all hidden tests pass | 8/10 | 7/10 |
| all hidden tests pass, excluding the `extra` test | **10/10** | **9/10** |
| check retries per run (spec / design / build / tests) | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0.2 (two runs needed one test retry) |
| agent calls per run | 4.0 | 1.2 |
| turns per run | 26 | 14 |
| tokens per run (in / out) | 270k / 21k | 235k / 13k |
| **cost per run** | **$0.0202** | **$0.0118** |
| total cost of the 10 runs | $0.202 | $0.118 |

Issues 1, 3, 4 and 5 gave the same hidden-test result in both modes (issue 5 fails only the `extra` test in all four runs). **The whole difference is issue 2.**

## What the one difference is
In `single_issue2_rep1` the agent **changed no source file**. Its own design says: "the fix contradicts an existing test that asserts the bug. Resolving it needs a maintainer decision (Q-01). Until then the issue is not fixed in code", and it wrote six tests marked `xfail` instead. That is the conservative, human-decision reading of an issue that asks to reverse a documented, tested contract (see `experiment/validation/README.md`). In the other three issue-2 runs the agents fixed the code and **rewrote the existing contract test** (`test_query_cache_documents_are_shared_with_cache`), as PR #14 did.

Two gaps in the pipeline's checks show up here:
1. The run finished **DONE**, with nothing in the status telling the maintainer that a decision was waiting. The design lint only demands that a `tinydb/` file is *listed*, not that it was changed; the suite "passes" because `xfail` tests do not fail.
2. So "all checks pass" and "the issue is resolved" are different things (this feeds the escalation policy: a design that lists an unapplied change or an unresolved conflict should reach a human).

## Conclusion
- **Cost:** the three-agent split costs about 70% more per run for stages 1 to 4 ($0.0202 vs $0.0118), because the Planner and the Builder each read the repository and pass files to each other.
- **Quality:** no difference that can be attributed to the split. 10/10 vs 9/10 excluding the `extra` test is one run out of ten, and that run is a deliberate non-fix of a contract-conflict issue, not an error. With 10 runs per variant this cannot show either variant is better.
- **ADR-001 therefore stays Accepted, but on other grounds.** This experiment does not measure what the author's reasons rest on (a read-only Planner, an independent Reviewer, code and tests in one Builder context), and `single` here still has the Builder's tools in the planning step. The honest statement is: the split has a measurable cost and no measured benefit in this experiment.
- **No design change** follows from it.

## Threats to validity
10 runs per variant and 5 issues; one model (Haiku); the single-agent prompt was written by me (it reuses the Planner and Builder instructions, which may favour either variant); stages 5 and 6 are excluded; hidden tests are mine; issue 5's reading of the answers is auto mode (assume). A first attempt of this experiment (run 45015554876, $0.422) was invalid because of a bug in my driver (artifacts written inside the repository, see `results/runs.md` row 26); an offline scorer bug (relative patch path) briefly showed 0/0 and was fixed before any number was taken.
