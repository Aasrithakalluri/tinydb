# ADR-001: Three agents (Planner, Builder, Reviewer); release is plain code

- **Author:** Aasritha Kalluri
- **Decision area:** D1 Splitting the work
- **Status:** Accepted. Tested in Experiment 1 (`results/exp1/README.md`): no quality difference attributable to the split (10/10 vs 9/10 runs pass the hidden tests excluding the `extra` test; the one difference is a deliberate non-fix of a contract-conflict issue), and the three-agent split costs about 70% more per run for stages 1 to 4 ($0.0202 vs $0.0118). The reasons for the split (read-only Planner, independent Reviewer, code and tests in one context) are not what this experiment measures. No design change.
- **Decided by:** me (Aasritha Kalluri). I chose this split in the design discussion (my answer was "1A") and gave the reasons below in a design interview on 2026-11-22. My coding assistant (Claude Code) wrote the wording from my answers.
- **Reviewed and adopted by:** Aasritha Kalluri, 2026-11-22

## Context
Six stages must be run. Stages 1-2 (spec, design) are read-only reasoning over the issue and `ARCHITECTURE.md`. Stages 3-4 (implement, test) both edit the same files and rely on each other's feedback (a failing test is only useful to whoever holds the code). Stage 6 must be independent of everything else. Stage 5 (push, open PR) is deterministic. My budget is $5 in total, so every extra agent costs context re-reading.

## Decision
I decided as follows.

I use three LLM agents: the **Planner** (stages 1-2, Haiku), the **Builder** (stages 3-4, Haiku) and the **Reviewer** (stage 6, Sonnet). Stage 5 is code in the orchestrator, with no LLM.


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **Planning is read-only.** Writing the spec and the design needs no code edits, so the Planner gets read-only tools.
- **The Reviewer must be independent.** If one agent did everything, the review would only repeat that agent's own thinking.
- **The Builder needs code and tests in one context.** When a test fails, the agent that wrote the code is the one that fixes it, so stages 3 and 4 stay together.
- **Cost.** Every extra agent re-reads the repository, so one agent per stage would cost more.

## Alternatives considered

I rejected these options:

- **One agent for everything:** cheapest, but the reviewer would share context with the implementer (violates independence) and one prompt must carry spec-writing, design and coding rules.
- **One agent per stage (five agents):** clean prompts, but stage 3 and 4 would pass code state back and forth through files with no shared memory of why the code looks as it does, and each agent re-reads the repo (cost).
- **One implementer for stages 1-4 plus a reviewer:** fewer handoffs; rejected because the spec/design stages benefit from read-only tools (the planner cannot change code it is only meant to describe).

## Consequences

What I accept with this decision:

+ Tool permissions follow the split: Planner cannot edit, Builder cannot see the reviewer, Reviewer cannot push.
+ Planner → Builder handoff is a natural check point (`design.md` lint).
− Planner and Builder do not share memory: any detail missing from `design.md` is lost. Mitigated by design lint and by letting the Builder read the repo.
− Haiku carries both planning and coding; weaker planning may surface as test/design loops (measured in Results).

## Result of Experiment 1 (2026-11-22)
Single agent vs three agents for stages 1 to 4, 20 runs, same model and checks: both variants completed 10/10 runs; hidden tests passed 10/10 (three agents) vs 9/10 (single agent) excluding the `extra` test; cost per run $0.0202 vs $0.0118. The one difference was a single-agent run that recognised a conflict with a documented contract and did not change the code (it wrote `xfail` tests), which the pipeline reported as DONE without telling the maintainer; this exposed a gap in the checks (a listed change need not be applied). Details: `results/exp1/README.md`.
