# ADR-011: On restart, restore state.json and re-apply diff.patch; reuse the open PR

- **Decision area:** D4 State (supersedes ADR-004)
- **Status:** Accepted

## Context
ADR-004 said a restarted run "downloads the latest artifact and resumes at the first stage whose check has not passed". The first real runs on issue #3 (Actions runs 44994878885, 44995093783, 44995270382) showed three things that were wrong:
1. A restarted run starts from a **fresh checkout of master**. Only `state.json` came back, not the code. The run resumed at RELEASE, committed *nothing*, and force-pushed an empty commit over `autose/issue-3`, so PR #10 briefly had 0 changed files while the state said "tests pass".
2. State was only saved at log points, so a crash between `gh pr create` and the next save lost the PR URL. The next restart tried to create a second PR and failed.
3. The CI wait matched the newest run for the head SHA, which was the `pull_request` run gated at `action_required`, not the `workflow_dispatch` run that actually executes.

## Decision
- The workflow artifact (`state.json` + stage artifacts, including `diff.patch`) remains the restart source of truth. On resume in IMPLEMENT/TEST/RELEASE/REVIEW, the orchestrator checks out the recorded `base_sha` on branch `autose/issue-N` and **re-applies `diff.patch`** before continuing.
- The release stage first looks up an **open PR for the branch** and reuses it; the PR URL is saved to state immediately after creation.
- CI results are taken only from the `workflow_dispatch` run for the head SHA.
- A redesign or reset to base empties `diff.patch`, so stale code cannot be re-applied.
- Any unexpected exception is converted into a FAILED stage with the error written into that stage's artifact.

## Alternatives considered
- **Fetch the branch from the remote instead of re-applying the patch:** simpler, but the branch can be overwritten (as happened), while the artifact is written per stage.
- **Commit state files to the branch:** durable, but pollutes the PR (rejected in ADR-004 already).

## Consequences
+ A restart is idempotent: same code, same PR, budgets preserved.
− Restart correctness now depends on `diff.patch` being applied cleanly to `base_sha`; if master moved, we still use the recorded base (the PR may then need a human rebase).
− The lesson for the report: the original ADR was reasoned but untested; one real run was enough to falsify it.

## Addendum 2026-11-22: "latest artifact" must mean newest by creation time
Found when answering the ask-mode questions on issue #5 (runs 45003888171 and 45003922512). The restore step took the first entry of the artifact list, but the GitHub artifacts API orders by artifact id, and ids are not in creation order. It restored the finished baseline run's state (DONE) instead of the paused ask run's state (WAITING), so `/autose go` did nothing, and the no-op runs re-uploaded the DONE state as the newest artifact. The restore now lists up to 100 artifacts, drops expired ones, and sorts by `created_at`. The two poisoned artifacts were deleted. This is a bug in the implementation of this decision, not a change to the decision.

## Addendum 2026-11-22 (2): restart rebases onto the current default branch
Found on the ask-mode run for issue #5 (PR #26): the repository CI failed on every job because `master` had gained `workflow/tests/` (which imports the agent SDK) after the run's recorded base commit, and a restart re-applied the patch on that old base, so the resumed run could not pick up the fix on `master`. On restart the orchestrator now checks whether `diff.patch` applies cleanly to the current default branch (`git apply --check`) and, if so, rebases onto it and records the new base; otherwise it keeps the recorded base. The same incident showed that `master` itself had been red since PR #22 (`pytest` collected the workflow's tests); `pytest.ini` now sets `testpaths = tests`.
