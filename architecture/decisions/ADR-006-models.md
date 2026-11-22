# ADR-006: Haiku for Planner and Builder, Sonnet for Reviewer

- **Author:** Aasritha Kalluri
- **Decision area:** D6 Models
- **Status:** Accepted
- **Decided by:** me (Aasritha Kalluri). My decision was "Haiku for the others and Sonnet for the reviewer"; the reasons below are mine, from the design interview of 2026-11-22. I did **not** give cost or Haiku's capability as a reason for the choice; the $5 limit is a fact about the setting.

## Context
Hard spend cap of $5 across setup, debugging, five issues and experiments (a fact about the setting). Roles differ in what a failure costs: a weak Builder costs retries (bounded by the orchestrator); a weak Reviewer lets bad code reach the human.

## Decision
- **Planner and Builder:** `claude-haiku-5-5`.
- **Reviewer:** `claude-sonnet-5-5`.


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **A different model for the reviewer.** The reviewer then does not share the implementer's bias, which gives a stronger independence argument than a different prompt alone.
- **The reviewer runs rarely.** It runs once or twice per run, so the stronger model is affordable there.

## Alternatives considered
- **Haiku everywhere:** the reviewer would share the Builder's model and its blind spots. Tested in Experiment 2: a Haiku reviewer with the implementer's artifacts caught 10/10 seeded defects against 8/10 for the independent Sonnet reviewer, at about 1/12 of the cost (`results/exp2_v2/README.md`).
- **Sonnet everywhere:** not tried (the setting's $5 limit).

## Consequences
+ Most tokens (reading, editing, retries) are on the cheap model.
− Haiku may fail on the vague issue or on cache-related bugs; measured per stage in Results.
− Model aliases/prices can change; exact model IDs and token counts are recorded per run in `results/results.csv`.
