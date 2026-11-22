# Runs log (every Actions run, PR and review; failures included)

Repo: https://github.com/Aasrithakalluri/tinydb

| # | Issue | Run | Result | Notes |
|---|-------|-----|--------|-------|
| 1 | - | [44994091231](https://github.com/Aasrithakalluri/tinydb/actions/runs/44994091231) | failure (0 s) | autose.yml invalid: `runner` context used in job-level `env`. Fixed in PR #9 (found with actionlint). |
| 2 | #3 | [44994878885](https://github.com/Aasrithakalluri/tinydb/actions/runs/44994878885) | failure at RELEASE | Stages 1-4 passed ($0.020). `gh pr create` refused: repo setting "Allow GitHub Actions to create pull requests" was off. |
| 3 | #3 | [44995093783](https://github.com/Aasrithakalluri/tinydb/actions/runs/44995093783) | failure at RELEASE | Restart resumed at RELEASE but code was not restored (empty commit pushed, PR #10 had 0 changes); CI wait matched a gated `pull_request` run (`action_required`). See ADR-011. |
| 4 | #3 | [44995270382](https://github.com/Aasrithakalluri/tinydb/actions/runs/44995270382) | failure at RELEASE | Worktree restore worked; second `gh pr create` failed because PR #10 already existed. |
| 5 | #3 | [44995345522](https://github.com/Aasrithakalluri/tinydb/actions/runs/44995345522) | **success (DONE)** | PR [#10](https://github.com/Aasrithakalluri/tinydb/pull/10), CI ok, Sonnet approved (round 1). Total $0.058, 298k in / 19k out tokens. Hidden tests 3/3 pass. Reviewer said it had not read ARCHITECTURE.md (prompt fixed afterwards). |
| 6 | #1 | [44996285044](https://github.com/Aasrithakalluri/tinydb/actions/runs/44996285044) | **success (DONE)** | PR [#15](https://github.com/Aasrithakalluri/tinydb/pull/15). $0.070, 428k in / 26k out. Sonnet approved round 1 (also checked constraints 4 and 5). Hidden tests 3/3, repo suite 242 passed. |
| 7 | #2 | [44996288135](https://github.com/Aasrithakalluri/tinydb/actions/runs/44996288135) | **success (DONE)** | PR [#14](https://github.com/Aasrithakalluri/tinydb/pull/14). $0.086, 359k in / 22k out. Deep-copy fix in `Table.search`. Sonnet approved and noted ARCHITECTURE.md ADR-3 wording is now stale. Hidden tests 3/3, suite 232 passed. |
| 8 | #4 | [44996291011](https://github.com/Aasrithakalluri/tinydb/actions/runs/44996291011) | failure at REQ | $0.013. Spec was fine; my AC regex did not accept tagged criteria `FR-03-AC1 (failure):` (pipeline bug). Fixed in ADR-012. |
| 9 | #5 | [44996293511](https://github.com/Aasrithakalluri/tinydb/actions/runs/44996293511) | failure at IMPLEMENT | $0.019. Design said "implementation must not start until Q-01 is resolved"; Builder made an empty diff. Pipeline had no path for vague issues. Fixed in ADR-012. |
