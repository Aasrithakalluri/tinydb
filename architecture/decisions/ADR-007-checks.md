# ADR-007: Deterministic checks decide pass/fail; LLMs never grade their own stage

- **Author:** Aasritha Kalluri
- **Decision area:** D7 Checks
- **Status:** Accepted
- **Decided by:** my coding assistant proposed the mechanism and I accepted it (PR #7). The reasons below are mine, selected in the design interview of 2026-11-22, together with my note on stage 6.
- **Reviewed and adopted by:** Aasritha Kalluri, 2026-11-22

## Context
A stage's own agent is a poor judge of its output. Checks must be cheap, reproducible and hard to talk around.

## Decision
I decided as follows.

The orchestrator runs every check as code (see `architecture/views/stage-map.md`):
- Stage 1: spec lint (AC IDs, `situation → result` form, banned vague words, ≥1 failure/boundary AC per requirement). "Testable" is approximated structurally.
- Stage 2: design lint (named files exist, named functions/classes found, only `tinydb/` and `tests/`, import-layering constraints from `ARCHITECTURE.md` §3.4).
- Stage 3: `compileall` + `import tinydb`; diff restricted to files in `design.md`.
- Stage 4: orchestrator runs `pytest` itself on the full suite; each AC ID must be referenced by a test.
- Stage 5: repo CI conclusion for the PR head SHA.
- Stage 6: structured verdict; "approve" is rejected if the reviewer's tool log has no test run.
The final pass/fail is always the orchestrator's, never an agent's. The final merge is the human's.


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **No second model to fool.** An LLM judge would be one more component that can be misled by the input.
- **Hard to talk around.** A check in code cannot be persuaded by a confident-sounding message.
- **Cheap and reproducible.** The same input always gives the same result and costs no tokens.
- **An agent must not grade its own stage.**

## My note on stage 6
I pointed out that stage 6 is **not purely deterministic**: its input is the Reviewer agent's verdict, an LLM output. The orchestrator still applies a code rule to that verdict and rejects "approve" when the Reviewer's tool log shows no test run. The checks of stages 1 to 5 are deterministic code; stage 6 is a deterministic rule applied to an LLM verdict, and the final pass or fail is the orchestrator's. (My note in the interview was cut off after "So the fi…"; this paragraph records only what I wrote and what this ADR already decided.)

## Alternatives considered

I rejected these options:

- **LLM judge per stage:** catches semantic problems (is this AC really testable?) but adds cost, noise and a second model to be fooled.
- **Trust the agent's own report:** cheapest, known to over-report success.

## Consequences

What I accept with this decision:

+ Cheap, reproducible, no extra tokens.
− Lint cannot judge whether an AC is *meaningfully* testable; weak ACs can pass (Limitations). Possible later addition: an LLM judge for stage 1 only.
− CI in stage 5: pull requests created with `GITHUB_TOKEN` do not reliably run the `pull_request` workflow (the run it creates is gated at `action_required`), so the orchestrator starts CI with `workflow_dispatch` and reads only that run. I verified this works in the real runs (ADR-011 records the bug that came from reading the wrong run).
