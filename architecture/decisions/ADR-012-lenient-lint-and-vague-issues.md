# ADR-012: Lenient AC parsing, and vague issues proceed on stated assumptions

- **Decision area:** D7 Checks and D2 Control flow (refines ADR-007 and ADR-002; neither is superseded)
- **Status:** Accepted for AC parsing. The rule "vague issues proceed on assumptions" is superseded by ADR-013 as the only behaviour: it remains the default in auto mode, and ask mode is added.
- **Decided by:** the assistant, after the runs on issues #4 and #5; reported to the author. Its vague-issue rule is superseded by ADR-013.

## Context
The first batch of runs on issues #1, #2, #4, #5 (runs 44996285044, 44996288135, 44996291011, 44996293511) produced two failures that were caused by the pipeline, not by the model:
1. **Issue #4, stage 1 rejected a good spec.** The Planner followed the A1 skill's template, which allows tagged criteria (`- FR-03-AC1 (failure): ...`). My stage-1 regex accepted only `- FR-03-AC1: ...`, so every tagged criterion was invisible and FR-02/FR-03 looked like they had none. The check was the defect. This is the weakness ADR-007 named (a regex only approximates "testable"), appearing sooner than expected.
2. **Issue #5 (vague), stage 3 produced an empty diff.** With no stakeholder available, the Planner's design said "Implementation must not start until Q-01 is resolved", and the Builder obeyed. The pipeline had no way to wait for or ask a human, so the run died at IMPLEMENT. The A1 skill's own rule is "document and continue", and the spec prompt already said so, but the design prompt did not repeat it.

## Decision
- The AC pattern accepts the skill's optional tag after the ID (`FR-01-AC3 (boundary):`) and bold IDs. Unit tests for all checks live in `workflow/tests/test_checks.py`, so lint changes are tested before they can block a run.
- **Open questions never block a stage.** The design prompt forbids "wait/postpone" wording and requires the assumed interpretation to be listed under Risks; the Builder prompt says an empty diff is a failure and to implement the assumed interpretation.
- The assumptions are made visible to the human instead of being resolved silently: the PR body embeds `spec.md` (which carries the ASM/open-question registers) and `design.md` in collapsible sections.
- `/autose fresh` starts a run that ignores restored state, so a changed prompt or check can be tried without inheriting an old design.

## Alternatives considered
- **Stop and ask on a vague issue:** honest, but there is nobody to answer during a run, and "stopped" produces no PR to judge. It stays an option for an experiment variant.
- **LLM judge for "is this criterion testable?":** more tolerant of format, but adds cost and a second model to fool (see ADR-007).

## Consequences
+ Format tolerance without loosening the real requirements (arrow form, no vague words, every requirement has criteria).
+ A vague issue yields a PR whose assumptions a human can accept or reject.
− A wrong assumption now ships as code; the reviewer sees the issue and diff but not the spec (ADR-003), so it may not notice. Measured on issue #5 in Results.
− Counting a run that proceeded on a guess as "success" can overstate quality; the report scores the vague issue separately.
