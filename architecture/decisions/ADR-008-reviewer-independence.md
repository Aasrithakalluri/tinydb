# ADR-008: Reviewer is isolated by context, model, prompt and permissions

- **Decision area:** D8 Reviewer independence
- **Status:** Accepted. Experiment 2 did **not** support its hypothesis that independence improves detection (independent reviewer 8/10 caught, shared-context reviewer 10/10); see `results/exp2_v2/README.md`. Independence is kept because the assignment requires it; ADR-014 changes the reviewer prompt in response.

## Context
A reviewer that sees the implementer's reasoning tends to agree with it. The brief requires: sees only issue, diff and repo at PR head; can run code; cannot push.

## Decision
- **Context:** fresh SDK session; input = issue text, `diff.patch`, and a *separate clean checkout* at the PR head SHA. No spec, design, test report, PR body, or Builder messages.
- **Model:** Sonnet (different from Builder's Haiku).
- **Prompt:** its own adversarial prompt: "assume the change is wrong until you have evidence; for each claim in the issue, try to reproduce it; run the full tests; try at least two inputs the author is unlikely to have tried; every finding must cite file:line and a command/output". Output is JSON: `verdict` (`approve` | `changes`), `issue_type` (`code` | `approach`), `findings[]`.
- **Permissions:** read + allowlisted Bash only; environment has no GitHub token; posting the review is done by the orchestrator.
- **Anti-rubber-stamp:** orchestrator rejects an `approve` with no executed test run; reviewer quality is measured on 5 seeded PRs with known defects (catch rate and false-positive rate reported).

## Alternatives considered
- **Same model, same context, "review your work":** cheapest; weakest independence.
- **Separate Actions job for the reviewer:** stronger permission isolation (own token), at the cost of cross-job state passing. Kept as future work.

## Consequences
+ Findings are evidence-based and reproducible.
− Without the spec the reviewer may disagree about a vague issue's meaning.
− Adversarial prompting can produce false positives and extra rounds (cost); measured.
