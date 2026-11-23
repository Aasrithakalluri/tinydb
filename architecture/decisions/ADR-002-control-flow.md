# ADR-002: One Python orchestrator as an explicit state machine

- **Author:** Aasritha Kalluri
- **Decision area:** D2 Control flow
- **Status:** Accepted
- **Decided by:** Aasritha Kalluri

## Context
The flow has loops (test retries, review rounds) and back-edges (to implementation or design). Someone must decide when to go back and when to stop, and that decision must be inspectable and bounded. GitHub Actions is good at triggering and permissions, poor at loops with counters.

## Decision
I decided as follows.

I use a single script, `workflow/orchestrator.py`, that runs the stages as a state machine with states `REQ → DESIGN → IMPLEMENT → TEST → RELEASE → REVIEW → DONE | FAILED`. **Deterministic code, not an LLM, decides transitions.** Rules:
- Check fails at stages 1-3: one retry of the same stage with the failure text; then FAILED with explanation in the stage artifact.
- Stage 4 fails: back to 3 (max 2 retries); after that back to 2 once; then FAILED.
- Stage 6 verdict `changes/code` → 3, `changes/approach` → 2; at most 2 review rounds in total, then stop and hand to the human with `review.md`.
The agents may *recommend* (reviewer labels an issue `code` or `approach`) but the orchestrator applies counters and budgets.

## Rationale
- **Code, not an agent, decides who goes back.** Loops and counters must be bounded and predictable.
- **One job, one place for state.** It is easier to follow and debug, and there is a single concurrency group.
- **No tokens spent on routing.** An LLM orchestrator would spend tokens on routing and could keep itself in a loop.
- **Actions jobs do not trigger each other.** Events created with `GITHUB_TOKEN` do not start new workflows, so a loop built from chained jobs is hard to make work.

## Alternatives considered

I rejected these options:

- **Separate Actions jobs that trigger each other:** natural isolation, but loops need workflow re-dispatch and `GITHUB_TOKEN` events do not trigger new workflows.
- **LLM orchestrator agent that decides next step:** flexible, but spends tokens on routing, can loop forever, and is hard to bound.
- **Fixed linear pipeline without back-edges:** simplest, but the assignment requires going back.

## Consequences

What I accept with this decision:

+ Bounded, testable control flow; every transition logged in `state.json`.
+ Whole run in one job, so one concurrency group and one timeout.
− Orchestrator is a single point of failure and holds the GitHub token (see ADR-005 for how agents are kept away from it).
− Less flexible than a planner: routing rules are my guess and may need change after runs (see Results).
