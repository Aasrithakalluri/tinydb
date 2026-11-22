# ADR-014: The independent reviewer must compare new code with its closest analogue; contract reversals are `approach` findings

- **Decision area:** D8 Reviewer independence (follows ADR-008, which stays Accepted)
- **Status:** Proposed. To be tested on new seeds that were not used to design it (see below); updated to Accepted or Superseded with the result.

## Context
Experiment 2 (`results/exp2_v2/README.md`) compared the independent Sonnet reviewer of ADR-008 with a Haiku reviewer that also sees the author's spec, design and test report. On seeded PRs the independent reviewer caught 8 of 10 defective reviews and the shared-context one 10 of 10; the only difference was S4 (`multiply` silently skipping a document that lacks the field). The independent reviewer **saw** the behaviour and accepted it because the issue never says what should happen; the sibling operations in the same file raise `KeyError`. The shared-context reviewer had the spec, which said so. Separately, neither reviewer treated the reversal of a documented, tested contract (S2 / PR #14) as something a human must decide.

## Decision
- Keep the independence rule of ADR-008 (the reviewer sees only the issue, the diff and the repository). Do **not** give it the author's spec, design or test report.
- Add two steps to the reviewer prompt: (1) *find the closest existing analogue of each new or changed function (siblings in the same module) and compare edge-case behaviour: missing input, wrong type, empty input, error type raised*; (2) *a change that removes assertions from an existing test, or contradicts a documented docstring/ADR, is a finding with `issue_type: approach`* so that the orchestrator routes it to design and the status comment names it for a human.
- The reviewer still returns the same JSON; the orchestrator rule that overrules an approval without a test run stays.

## Alternatives considered
- **Give the reviewer the spec (variant B):** best detection in the experiment and 12 times cheaper, but violates the assignment's independence requirement and lets the author's assumptions leak into the review. Rejected on those grounds, not on the measured results.
- **Let the Planner's acceptance criteria (not the whole spec) reach the reviewer:** a possible middle path; not tested, listed as future work.
- **Do nothing and accept the miss:** the S4 class (silent behaviour that differs from sibling code) is common in real changes.

## How this will be tested
New seeds not used to design the change: S6 (a different sibling-consistency defect, in another operation or method), S7 (a removed assertion in an existing test), C3 (a correct change). Success criterion fixed before the run: the independent reviewer catches S4, S6, S7 with no false rejection of the controls. If S4 is caught but S6/S7 are not, the change is overfitted to S4 and this ADR is superseded.

## Consequences
+ Keeps independence while covering the one defect class the experiment showed it missing.
− Longer reviewer prompt and a few more turns (cost).
− The comparison step may also produce false rejections (the sibling may itself be wrong); measured on the controls.
