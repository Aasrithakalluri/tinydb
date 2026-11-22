# ADR-007: Deterministic checks decide pass/fail; LLMs never grade their own stage

- **Decision area:** D7 Checks
- **Status:** Accepted

## Context
A stage's own agent is a poor judge of its output. Checks must be cheap, reproducible and hard to talk around.

## Decision
The orchestrator runs every check as code (see `architecture/views/stage-map.md`):
- Stage 1: spec lint (AC IDs, `situation → result` form, banned vague words, ≥1 failure/boundary AC per requirement). "Testable" is approximated structurally.
- Stage 2: design lint (named files exist, named functions/classes found, only `tinydb/` and `tests/`, import-layering constraints from `ARCHITECTURE.md` §3.4).
- Stage 3: `compileall` + `import tinydb`; diff restricted to files in `design.md`.
- Stage 4: orchestrator runs `pytest` itself on the full suite; each AC ID must be referenced by a test.
- Stage 5: repo CI conclusion for the PR head SHA.
- Stage 6: structured verdict; "approve" is rejected if the reviewer's tool log has no test run.
The final pass/fail is always the orchestrator's, never an agent's. The final merge is the human's.

## Alternatives considered
- **LLM judge per stage:** catches semantic problems (is this AC really testable?) but adds cost, noise and a second model to be fooled.
- **Trust the agent's own report:** cheapest, known to over-report success.

## Consequences
+ Cheap, reproducible, no extra tokens.
− Lint cannot judge whether an AC is *meaningfully* testable; weak ACs can pass (Limitations). Possible later addition: an LLM judge for stage 1 only.
− CI in stage 5: PRs created with `GITHUB_TOKEN` do not trigger `pull_request` workflows, so CI will be started with `workflow_dispatch` (to be verified in Phase 3; ADR to be superseded if this does not work).
