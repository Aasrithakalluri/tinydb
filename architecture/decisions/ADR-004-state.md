# ADR-004: State in stage-artifact files, branch, and an issue status comment

- **Author:** Aasritha Kalluri
- **Decision area:** D4 State
- **Status:** Superseded by ADR-011 (restart rule was wrong: restoring state.json alone does not restore the code)
- **Decided by:** my coding assistant proposed the mechanism and I accepted it (PR #7). The reasons below are mine, selected in the design interview of 2026-11-22. Superseded by ADR-011 after real runs falsified the restart rule.

## Context
Runs can be restarted (re-labelled, `/autose` again, job cancelled by timeout). Humans must be able to follow progress on GitHub. Actions runners are ephemeral.

## Decision
- **Within a run:** `.autose/issue-N/` directory with `state.json` (current state, counters, SHAs) and the stage artifacts `spec.md`, `design.md`, `diff.patch`, `test_report.md`, `pr.md`, `review.md`.
- **Across runs / for humans:** the artifact directory is uploaded as a workflow artifact after every stage (so a cancelled run still leaves its work), code lives on branch `autose/issue-N`, and the orchestrator maintains **one status comment** on the issue (edited in place) with stage results and links.
- **Restart rule:** a new run for the same issue downloads the latest artifact of that issue, and resumes at the first stage whose check has not passed. Counters (retries, review rounds) are restored from `state.json` so restarts cannot reset budgets.
- No cache is used for state (caches are evictable and not visible to humans).


## Why (my reasons)
Recorded from my answers in the design interview of 2026-11-22; each point below is a reason I selected.
- **Anyone can follow a run on GitHub.** Status comment, artifacts, branch and pull request are all visible without special access.
- **A cancelled run still leaves its work.** The artifacts are uploaded after every stage.
- **The cache can be evicted.** For that reason the cache is not used as the place for state.
- **Restarts must not reset the budgets.** Counters (retries, review rounds, cost) are restored from the saved state, so a restart cannot be used to spend more.

## Alternatives considered
- **Commit artifacts to the branch:** durable and diffable, but pollutes the PR with process files.
- **PR comments only:** visible, but hard to parse and edit reliably, and the PR does not exist before stage 5.
- **Actions cache:** fast, but may be evicted and not auditable.

## Consequences
+ Anyone can follow a run via the issue comment, artifacts, branch and PR.
+ Idempotent restarts with preserved budgets.
− Artifacts expire (retention set to 30 days; final evidence is copied to `results/`).
− State download adds an API call and depends on artifact retention.
