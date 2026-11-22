# ADR-014: The independent reviewer must compare new code with its closest analogue; contract reversals are `approach` findings

- **Decision area:** D8 Reviewer independence (follows ADR-008, which stays Accepted)
- **Status:** Proposed. Tested against its pre-registered criterion (`results/adr014_test/README.md`): criteria 1 and 2 met, criterion 3 not met (one correct control, C2, was rejected twice), so by the decision rule it stays Proposed and the production prompt is **not** changed. Not Accepted, not Superseded.
- **Decided by:** the assistant proposed it after Experiment 2; the author asked for the new seeds and the updated prompt to be built ("build S6, S7, C3 and update the reviewer prompt"). Not adopted.

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
Pre-registered in `experiment/seeded_prs/v3/PREREGISTRATION.md` (committed before any result). New seeds not used to design the change: **S6** (hash tag copied from a sibling operator), **S7** (unrequested reversal of the documented `remove(doc_ids=...)` rule with the three pinning tests rewritten), **C3** (correct control); plus S4, C1, C2. Two reviews per seed. Criterion: the new prompt (variant A2) returns `changes` on S4, S6 and S7 in both runs, identifies S7 as a reversal of documented behaviour (`issue_type: approach` or an explicit finding), and approves C1, C2, C3 in both runs. The current prompt (A) is run on S6, S7, C3 as the counterfactual. If S4 is caught but S6 or S7 is not, the change is overfitted to S4 and this ADR is superseded.

## Consequences
+ Keeps independence while covering the one defect class the experiment showed it missing.
− Longer reviewer prompt and a few more turns (cost).
− The comparison step may also produce false rejections (the sibling may itself be wrong); measured on the controls.

## Result of the test (2026-11-22)
- A2 caught S4, S6 and S7 in all six reviews and labelled the documented-rule reversal (S7) `approach`; it approved C1 and C3, and **rejected C2 twice** because `multiply` has stricter type validation than its siblings (defensible given the issue's "same style as the other operations", but it counts as a false rejection under the rule fixed in advance).
- The old prompt already caught S6 and S7 (verdict level), so the new seeds did not discriminate the prompts. The measurable gain is S4 (design seed) and the `approach` routing of S7.
- Steps 6 and 7 were tested together and cannot be separated. Not tuned further on C2 to avoid fitting the prompt to a single test case. Next test, if budget allows: step 7 alone on fresh seeds.
