# AutoSE — agentic SDLC workflow on a tinydb fork (Assignment 3)

- **Fork:** https://github.com/Aasrithakalluri/tinydb (upstream: msiemens/tinydb — never touched)
- **Pinned commit:** `edff96aeb2616402e9489d46e90a592c05565621` (`edff96a`)
- **Default branch:** `master` (protected: changes only via pull request)
- **Trigger:** add the label `autose` to an issue, or comment `/autose` (maintainers only)
- **Models:** Planner + Builder `claude-haiku-5-5`, Reviewer `claude-sonnet-5-5` (see architecture/decisions/ADR-006)
- **AI assistance:** Claude Code helped with scaffolding; ADRs and reasoning are the author's own. (Updated as work proceeds.)

**How to trigger:** add the label `autose` to an issue, or comment `/autose` (maintainers only). `/autose fresh` ignores state from earlier runs of the same issue.

Status: pipeline built and running; see `results/runs.md`. See `assignment.md` and `progress.md` for the plan.
