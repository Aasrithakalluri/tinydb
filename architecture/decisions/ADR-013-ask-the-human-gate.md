# ADR-013: A maintainer can choose "ask first": the run pauses, posts questions, and resumes on `/autose go`

- **Author:** Aasritha Kalluri
- **Decision area:** D2 Control flow, D10 Triggers (refines ADR-002 and ADR-010; supersedes the vague-issue rule of ADR-012)
- **Status:** Accepted (compared against the "assume" behaviour on issue #5; see `experiment/variants.md`)
- **Decided by:** Aasritha Kalluri

## Context
ADR-012 made vague issues proceed on a stated assumption, because during a run nobody can answer. I pointed out the better design: the pipeline should **ask me** (the human in the loop), and I will give the green flag. This also matches the A1 skill (ask the P1 questions when a stakeholder is present) and the assignment's principle that humans own the decisions that matter. The cost of guessing is real: a wrong assumption turns into a wrong PR, and the reviewer does not see the spec (ADR-003), so it may not catch it.

## Decision
I decided as follows.

- Two modes, chosen by the maintainer per issue:
  - **auto** (label `autose`, or `/autose`): as before; open questions are assumptions listed in the PR (ADR-012).
  - **ask** (`/autose ask`): after stage 1 the Planner must append "Questions for the maintainer" (at most 5 P1 questions with options). The orchestrator checks the spec as usual, posts the questions as an issue comment, sets state `WAITING`, and ends the run successfully. No design or code is produced and no further cost is spent while waiting.
- **Resume:** the maintainer replies `/autose go <answers>` (a bare `/autose go` means "go ahead with your assumptions"). The orchestrator restores state from the artifact, runs the Planner once more in revision mode (skill section 10: answers become CONFIRMED, IDs are kept), and continues through design, build, test, release, and review. Any other trigger while `WAITING` just posts "still waiting".
- Only users with write access can answer (same authorization as ADR-010). The answers are wrapped as data (`<maintainer_answers>`) and cannot change the Planner's output rules.
- The gate happens once per issue (`asked` flag), so a run cannot ask forever.

## Rationale
- **A wrong guess becomes a wrong pull request.** And the reviewer does not see the spec, so it may not notice a wrong assumption.
- **The human owns what the issue means.** The maintainer decides the intent of an unclear request.
- **It matches the A1 skill.** The skill says to ask the priority-1 questions when a stakeholder is available.
- **No cost while waiting.** The run ends after the spec and resumes later from its saved state.

## Alternatives considered

I rejected these options:

- **Always ask when the spec has open P1 questions:** the first runs showed that Haiku marks even clear issues "NOT READY" (issue #4), so this would stall most runs. Letting the maintainer decide per issue keeps clear issues fully automatic.
- **LLM decides whether the issue is vague:** one more judgement that can be wrong; the maintainer already knows.
- **Wait inside the job for the reply:** wastes runner time and hits the job timeout; ending and resuming from the artifact costs nothing while waiting.

## Consequences

What I accept with this decision:

+ The vague issue's intent is decided by a human, and is recorded in the issue thread.
+ Zero spend while waiting; restart logic (ADR-011) is reused.
− Not fully autonomous: ask mode needs a human round-trip (latency is unbounded).
− A second `/autose go` after the run has moved on is ignored (state is no longer `WAITING`).
− The gate only exists for stage 1; a wrong design is only caught by tests, the reviewer, or the human at merge time.
