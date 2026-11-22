# ADR-008: Reviewer is isolated by context, model, prompt and permissions

- **Author:** Aasritha Kalluri
- **Decision area:** D8 Reviewer independence
- **Status:** Accepted. Experiment 2 did **not** support its hypothesis that independence improves detection (independent reviewer 8/10 caught, shared-context reviewer 10/10); see `results/exp2_v2/README.md`. Independence is kept because the assignment requires it; ADR-014 changes the reviewer prompt in response.
- **Decided by:** me (Aasritha Kalluri). The four mechanisms below are the ones I selected in the design interview of 2026-11-22 (fresh context, adversarial prompt, the reviewer must run the tests, a different model with no push), and I chose to test this decision. My coding assistant wrote the exact prompt wording and the rule that overrules an approval without a test run, and I accepted them (PR #7).

## Context
A reviewer that sees the implementer's reasoning tends to agree with it. The brief requires: sees only issue, diff and repo at PR head; can run code; cannot push.

## Decision
- **Context:** fresh SDK session; input = issue text, `diff.patch`, and a *separate clean checkout* at the PR head SHA. No spec, design, test report, PR body, or Builder messages.
- **Model:** Sonnet (different from Builder's Haiku).
- **Prompt:** its own adversarial prompt: "assume the change is wrong until you have evidence; for each claim in the issue, try to reproduce it; run the full tests; try at least two inputs the author is unlikely to have tried; every finding must cite file:line and a command/output". Output is JSON: `verdict` (`approve` | `changes`), `issue_type` (`code` | `approach`), `findings[]`.
- **Permissions:** read + allowlisted Bash only; environment has no GitHub token; posting the review is done by the orchestrator.
- **Anti-rubber-stamp:** orchestrator rejects an `approve` with no executed test run; reviewer quality is measured on 5 seeded PRs with known defects (catch rate and false-positive rate reported).


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **Fresh context.** The reviewer sees only the issue, the diff and the repository, never the implementer's conversation or reasoning.
- **Adversarial prompt.** It starts from the assumption that the change is wrong until it has evidence.
- **It must run the tests itself.** An approval without an executed test run is not accepted.
- **A different model, and no push.** Sonnet reviews; it is allowed to read and run code but has no permission to push.

## Alternatives considered
- **Same model, same context, "review your work":** cheapest; weakest independence.
- **Separate Actions job for the reviewer:** stronger permission isolation (own token), at the cost of cross-job state passing. Kept as future work.

## Consequences
+ Findings are evidence-based and reproducible.
− Without the spec the reviewer may disagree about a vague issue's meaning.
− Adversarial prompting can produce false positives and extra rounds (cost); measured.

## My view after Experiment 2
Recorded from my answers of 2026-11-22. After the negative result (independent Sonnet reviewer 8/10 seeded defects caught; Haiku reviewer that also saw the implementer's artifacts 10/10, at about 1/12 of the cost) I want this ADR and the report to:
- **keep independence and report the negative result** (the assignment requires an independent reviewer, and the result is stated plainly: independence did not improve detection here);
- say that **independence is a rule, not a proven benefit** (this ADR's status above is worded that way);
- mention **shared context as future work**, for example giving the reviewer the acceptance criteria but not the implementer's reasoning;
- **retry ADR-014 later with its two prompt steps split**, because they were tested together.
