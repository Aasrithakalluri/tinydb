# ADR-006: Haiku for Planner and Builder, Sonnet for Reviewer

- **Decision area:** D6 Models
- **Status:** Accepted

## Context
Hard spend cap of $5 across setup, debugging, five issues and experiments. Roles differ in what failure costs: a weak Builder costs retries (bounded by the orchestrator); a weak Reviewer lets bad code reach the human.

## Decision
- **Planner and Builder:** `claude-haiku-5-5` (cheap, fast, fine for structured spec/design and small edits to a 700-line library).
- **Reviewer:** `claude-sonnet-5-5` (stronger reasoning, used once or twice per run on a small diff).
Using a different model family tier for the reviewer also reduces correlated blind spots between author and reviewer.

## Alternatives considered
- **Haiku everywhere:** cheapest; the reviewer would share the Builder's blind spots. (Tested in Experiment 2.)
- **Sonnet everywhere:** likely best quality, likely exhausts the $5 budget.

## Consequences
+ Most tokens (reading, editing, retries) are on the cheap model.
− Haiku may fail on the vague issue or on cache-related bugs; measured per stage in Results.
− Model aliases/prices can change; exact model IDs and token counts are recorded per run in `results/results.csv`.
