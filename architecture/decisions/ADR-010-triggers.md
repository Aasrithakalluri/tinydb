# ADR-010: Maintainer-only triggers, one run per issue at a time

- **Author:** Aasritha Kalluri
- **Decision area:** D10 Triggers
- **Status:** Accepted
- **Decided by:** my coding assistant proposed the mechanism and I accepted it (PR #7). The reasons below are mine, selected in the design interview of 2026-11-22.

## Context
Anyone can open issues or comment on a public fork. Starting the pipeline spends money and opens PRs, so it must be restricted. Duplicate triggers (label added twice, comment spam) must not run in parallel on the same branch.

## Decision
- **Events:** `issues: [labeled]` where the label is `autose`; `issue_comment: [created]` where the body, trimmed, starts with `/autose` (on an issue: start/resume; on a PR created by AutoSE: resume at review).
- **Authorization:** the job's first step checks the triggering actor (`github.event.sender` / comment author) has `write` or `admin` permission via the collaborators-permission API; otherwise it exits without using any secret or tool.
- **Concurrency:** `concurrency: group: autose-issue-${{ number }}, cancel-in-progress: false` so a second trigger queues behind the first rather than cancelling or racing; a queued run first reads `state.json` and exits as no-op if the issue is already DONE.
- **Fork safety:** the workflow only triggers on the fork's own events, never on pull requests from other repositories, so secrets are available and untrusted PR code is not executed with them.


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **Only maintainers may spend money and open pull requests.** Anyone can comment on a public repository, so the triggering user's permission is checked before anything else.
- **Two runs on one issue must not race.** A second trigger waits instead of running in parallel or cancelling a run that may be pushing.
- **Labels and comments are how maintainers work.** It matches the assignment's trigger and needs no extra tool.
- **Secrets and fork safety.** Only events of the fork itself start a run, never pull requests from other repositories.

## Alternatives considered
- **`workflow_dispatch` only:** safest, but not label/comment driven as required.
- **`cancel-in-progress: true`:** cheaper on duplicates but can kill a run mid-push.
- **Allow any commenter:** convenient, unacceptable for cost and safety.

## Consequences
+ Cost and write access limited to maintainers; no racing runs.
− Comment-triggered runs are slightly slower to start (permission API call).
− A maintainer account compromise is outside this design's protection.
