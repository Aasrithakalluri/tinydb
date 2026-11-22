# ADR-009: Hard budgets at every level; issue text is untrusted data

- **Decision area:** D9 Safety and failures
- **Status:** Accepted

## Context
$5 total spend, Actions timeouts, loops that can spin, and issue/comment text written by anyone.

## Decision
**Budgets and limits**
- Per agent call: `max_turns` (Planner 15, Builder 40, Reviewer 25) and a USD cap from SDK; per run: a cumulative cap of $0.60 tracked in `state.json` (run stops with FAILED when exceeded).
- Loop counters: stage retries 1, test→implement retries 2, redesign 1, review rounds 2 (restored on restart).
- Job `timeout-minutes: 40`; each pytest call has a 120 s timeout; a stage with no progress for 10 min is aborted.
- On any stop the stage artifact states why; the status comment shows FAILED/STOPPED with the reason.

**Prompt injection**
- Issue text is passed only as data inside `<untrusted_issue>` tags with an instruction that nothing inside is a command; never interpolated into shell, YAML or file paths (read via the event JSON file).
- Agents have no secrets and no network/GitHub tools (ADR-005); worst case is a wrong diff, which stage checks, tests and the human reviewer still see.
- Only users with write access can start a run (ADR-010), but their issues may quote hostile text, so the above still applies.
- Reviewer must treat code comments and PR text as data.

**Actions limits:** one job, artifacts kept ≤ a few MB, concurrency group per issue.

## Alternatives considered
- Provider-side limit only: required anyway ($5 cap) but gives no per-run stopping.
- Sandboxed VM/container per agent: stronger, more setup than the timeline allows.

## Consequences
+ Predictable worst-case cost per run (~$0.60) and bounded loops.
− Hard caps can stop a run that would have succeeded with one more turn.
− Python `-c` in allowlist is a residual escape hatch (documented).

## Addendum 2026-11-22: evidence from real runs
- **Budget cap works.** With the cap set to $0.02 the run stopped before the reviewer started (spent $0.016) and wrote the reason into `review.md`. It exposed a gap: the PR stayed open and looked finished. The orchestrator now comments on the PR when a run stops after the PR exists.
- **Prompt injection resisted (one attack).** See `experiment/security/results.md`. The evidence is for one direct injection in one run; indirect injection and weaker models are untested.
- **Fault injection is a test tool, not a feature:** the repo variable `AUTOSE_INJECT` is normally unset; every injected run is labelled in `results/runs.md`.
