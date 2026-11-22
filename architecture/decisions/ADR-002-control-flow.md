# ADR-002: One Python orchestrator as an explicit state machine

- **Decision area:** D2 Control flow
- **Status:** Accepted
- **Decided by:** **the author.** Their answer was "use a single python orchestrator script". The retry counts and routing rules (2 test retries, 1 redesign, 2 review rounds) were proposed by the assistant and accepted (PR #7).

## Context
The flow has loops (test retries, review rounds) and back-edges (to implementation or design). Someone must decide when to go back and when to stop, and that decision must be inspectable and bounded. GitHub Actions is good at triggering and permissions, poor at loops with counters.

## Decision
A single script, `workflow/orchestrator.py`, runs the stages as a state machine with states `REQ → DESIGN → IMPLEMENT → TEST → RELEASE → REVIEW → DONE | FAILED`. **Deterministic code, not an LLM, decides transitions.** Rules:
- Check fails at stages 1-3: one retry of the same stage with the failure text; then FAILED with explanation in the stage artifact.
- Stage 4 fails: back to 3 (max 2 retries); after that back to 2 once; then FAILED.
- Stage 6 verdict `changes/code` → 3, `changes/approach` → 2; at most 2 review rounds in total, then stop and hand to the human with `review.md`.
The agents may *recommend* (reviewer labels an issue `code` or `approach`) but the orchestrator applies counters and budgets.

## Alternatives considered
- **Separate Actions jobs that trigger each other:** natural isolation, but loops need workflow re-dispatch and `GITHUB_TOKEN` events do not trigger new workflows.
- **LLM orchestrator agent that decides next step:** flexible, but spends tokens on routing, can loop forever, and is hard to bound.
- **Fixed linear pipeline without back-edges:** simplest, but the assignment requires going back.

## Consequences
+ Bounded, testable control flow; every transition logged in `state.json`.
+ Whole run in one job, so one concurrency group and one timeout.
− Orchestrator is a single point of failure and holds the GitHub token (see ADR-005 for how agents are kept away from it).
− Less flexible than a planner: routing rules are my guess and may need change after runs (see Results).
