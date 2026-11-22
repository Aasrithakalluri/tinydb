# ADR-001: Three agents (Planner, Builder, Reviewer); release is plain code

- **Decision area:** D1 Splitting the work
- **Status:** Accepted, **untested**: the planned Experiment 1 (single agent vs three agents for stages 1 to 4) could not run because the API credit was exhausted (`results/runs.md`, run 45010442196, no valid data). The split is supported only indirectly: the tool policy and the independent reviewer depend on it, and 5 of 5 final runs passed the stage checks with it. Nothing in the evidence shows it is better than one agent.

## Context
Six stages must be run. Stages 1-2 (spec, design) are read-only reasoning over the issue and `ARCHITECTURE.md`. Stages 3-4 (implement, test) both edit the same files and rely on each other's feedback (a failing test is only useful to whoever holds the code). Stage 6 must be independent of everything else. Stage 5 (push, open PR) is deterministic. Budget is $5 in total, so every extra agent costs context re-reading.

## Decision
Three LLM agents: **Planner** (stages 1-2, Haiku), **Builder** (stages 3-4, Haiku), **Reviewer** (stage 6, Sonnet). Stage 5 is code in the orchestrator, no LLM.

## Alternatives considered
- **One agent for everything:** cheapest, but the reviewer would share context with the implementer (violates independence) and one prompt must carry spec-writing, design and coding rules.
- **One agent per stage (five agents):** clean prompts, but stage 3 and 4 would pass code state back and forth through files with no shared memory of why the code looks as it does, and each agent re-reads the repo (cost).
- **One implementer for stages 1-4 plus a reviewer:** fewer handoffs; rejected because the spec/design stages benefit from read-only tools (the planner cannot change code it is only meant to describe).

## Consequences
+ Tool permissions follow the split: Planner cannot edit, Builder cannot see the reviewer, Reviewer cannot push.
+ Planner → Builder handoff is a natural check point (`design.md` lint).
− Planner and Builder do not share memory: any detail missing from `design.md` is lost. Mitigated by design lint and by letting the Builder read the repo.
− Haiku carries both planning and coding; weaker planning may surface as test/design loops (measured in Results).
