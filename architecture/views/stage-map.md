# Stage map

| # | Stage | Who runs it | Model | Artifact | Check (who decides pass/fail) |
|---|-------|-------------|-------|----------|--------------------------------|
| 1 | Requirements | Planner agent (A1 skill) | Haiku | `spec.md` | Orchestrator lint: every acceptance criterion has an ID, a `situation → result` form, no banned vague words, at least one boundary/failure case. |
| 2 | Design | Planner agent (A2 `ARCHITECTURE.md`) | Haiku | `design.md` | Orchestrator lint: every named file exists in the repo, every named function/class is found in that file, lists no file outside `tinydb/` and `tests/`; checks the A2 layering constraints are not violated (import graph). |
| 3 | Implementation | Builder agent | Haiku | `diff.patch` | Orchestrator: `python -m compileall tinydb` and `import tinydb` succeed; diff touches only files listed in `design.md`. |
| 4 | Testing | Builder agent | Haiku | `test_report.md` | Orchestrator runs `pytest` itself (does not trust the agent's claim): all old + new tests pass; each acceptance criterion ID appears in a test name or docstring. |
| 5 | Release | Orchestrator code (no LLM) | — | `pr.md` + PR link | PR exists, branch pushed, repo CI run for the PR head SHA concludes `success`. |
| 6 | Review | Reviewer agent (independent) | Sonnet | `review.md` | Reviewer returns a structured verdict; orchestrator accepts "approve" only if the reviewer actually ran the tests; max 2 review rounds. Human merges. |
