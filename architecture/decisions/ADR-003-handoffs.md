# ADR-003: Hand off artifacts plus repo access, not conversations

- **Decision area:** D3 Hand-offs
- **Status:** Accepted
- **Decided by:** the assistant proposed the mechanism (PR #7); **the reasons below are the author's**, selected in the interview of 2026-11-22.

## Context
Agents have limited context and small budgets. What an agent sees also determines its bias: an implementer's reasoning primes a reviewer to agree.

## Decision
Every agent starts with a fresh context and receives only files:

| Agent | Receives | Deliberately NOT given |
|-------|----------|------------------------|
| Planner (stage 1) | issue title+body (wrapped as untrusted data), skill | repo code beyond what it reads itself, any other artifact |
| Planner (stage 2) | `spec.md`, `ARCHITECTURE.md`, read access to repo | the raw issue discussion/comments |
| Builder (3-4) | `design.md`, acceptance-criteria list from `spec.md`, repo working tree; on retries only the failing test output or reviewer findings | the Planner's conversation, the open-questions register |
| Reviewer (6) | issue text, `diff.patch`, clean checkout at PR head SHA | `spec.md`, `design.md`, Builder messages, test_report, PR description |

Artifacts are the contract; no agent receives another agent's chat transcript.


## Why (the author's reasons)
Recorded from the author's answers in the design interview of 2026-11-22; each point below is a reason the author selected.
- **It keeps the reviewer independent.** The reviewer never receives the implementer's conversation or reasoning.
- **Smaller prompts and lower cost.** Passing full transcripts would be huge and expensive.
- **Humans can inspect the artifacts.** `spec.md`, `design.md`, `diff.patch` and the others are the contract between stages and are readable by anyone following the run.
- **Summaries carry the previous agent's framing.** A summary written by the previous agent can hide exactly the awkward facts, so summaries are not handed over either.

## Alternatives considered
- **Pass full transcripts:** maximal information, but huge token cost and contaminates the reviewer.
- **Summaries written by the previous agent:** cheap, but summaries carry the previous agent's framing and can omit exactly the awkward facts.

## Consequences
+ Independence of the reviewer by construction; small prompts (cost).
+ Handoffs are reviewable by humans as artifacts.
− The Builder may miss intent that lives only in the issue; mitigated because ACs derive from the issue and the Builder may read it.
− Reviewer without the spec may judge against a different interpretation of a vague issue (see Limitations).
