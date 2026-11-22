# Decision-experiment variants

Each experiment changes **one** thing and runs on the same issues (target: all 5; fewer if budget runs out, stated in the report).

## Experiment 1 — ADR-001 (splitting the work)
| Variant | What changes |
|---------|--------------|
| **A (baseline)** | Planner (stages 1-2) + Builder (3-4) + Reviewer (6), as designed. |
| **B** | A single Haiku agent does stages 1-4 in one session (one prompt, one context). Reviewer unchanged. |

Hypothesis: B is cheaper (fewer tokens) but worse on stage-2 design lint and on hidden tests. Metrics: stage pass rates, hidden-test pass, tokens/cost per run, number of retries.

## Experiment 2 — ADR-008 (reviewer independence)
Run on the 5 seeded PRs (`experiment/seeded_prs/`, each with a known defect, plus one clean PR if possible).
| Variant | What changes |
|---------|--------------|
| **A (baseline)** | Sonnet reviewer, fresh context, adversarial prompt, must run tests. |
| **B** | Haiku reviewer that also receives the implementer's spec, design and test report (shared context), neutral prompt. |

Hypothesis: B approves more defective PRs. Metrics: defect catch rate, false-approve rate, false-reject rate, tokens/cost.

Negative or null results are reported as such.
