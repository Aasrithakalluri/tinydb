# ADR-010: Maintainer-only triggers, one run per issue at a time

- **Decision area:** D10 Triggers
- **Status:** Accepted
- **Decided by:** the assistant proposed it; the author accepted it by merging the design (PR #7).

## Context
Anyone can open issues or comment on a public fork. Starting the pipeline spends money and opens PRs, so it must be restricted. Duplicate triggers (label added twice, comment spam) must not run in parallel on the same branch.

## Decision
- **Events:** `issues: [labeled]` where the label is `autose`; `issue_comment: [created]` where the body, trimmed, starts with `/autose` (on an issue: start/resume; on a PR created by AutoSE: resume at review).
- **Authorization:** the job's first step checks the triggering actor (`github.event.sender` / comment author) has `write` or `admin` permission via the collaborators-permission API; otherwise it exits without using any secret or tool.
- **Concurrency:** `concurrency: group: autose-issue-${{ number }}, cancel-in-progress: false` so a second trigger queues behind the first rather than cancelling or racing; a queued run first reads `state.json` and exits as no-op if the issue is already DONE.
- **Fork safety:** the workflow only triggers on the fork's own events, never on pull requests from other repositories, so secrets are available and untrusted PR code is not executed with them.

## Alternatives considered
- **`workflow_dispatch` only:** safest, but not label/comment driven as required.
- **`cancel-in-progress: true`:** cheaper on duplicates but can kill a run mid-push.
- **Allow any commenter:** convenient, unacceptable for cost and safety.

## Consequences
+ Cost and write access limited to maintainers; no racing runs.
− Comment-triggered runs are slightly slower to start (permission API call).
− A maintainer account compromise is outside this design's protection.
