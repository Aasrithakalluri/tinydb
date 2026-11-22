# AutoSE: an agentic SDLC workflow on a tinydb fork (Assignment 3)

A maintainer labels an issue `autose` (or comments `/autose`); agents write the spec and the design, change the code, test it, open a pull request, and a separate reviewer agent reviews it. **A human decides whether to merge; the workflow never merges.**

- **Fork:** https://github.com/Aasrithakalluri/tinydb (upstream `msiemens/tinydb` is never touched)
- **Pinned commit:** `edff96aeb2616402e9489d46e90a592c05565621` (`edff96a`); the fork's default branch is `master`, protected (changes only by pull request)
- **Models:** Planner and Builder `claude-haiku-5-5`; Reviewer `claude-sonnet-5-5` (via the Claude Agent SDK)
- **Report / video:** `report.pdf`, `demo.mp4` (see the end of this file for what is still missing)

## How to trigger it
| Action | Effect |
|---|---|
| add the label `autose` to an issue | start a run (only users with write access; anyone else is refused) |
| comment `/autose` on an issue | start or resume a run |
| comment `/autose ask` | after the spec the run pauses and posts up to 5 questions on the issue |
| comment `/autose go <answers>` | resume a paused run with the maintainer's answers (a bare `/autose go` accepts the assumptions) |
| comment `/autose fresh` | ignore the state of earlier runs of this issue |

One run per issue at a time (a second trigger queues). Follow a run through the status comment on the issue, the workflow artifacts (`spec.md`, `design.md`, `diff.patch`, `test_report.md`, `pr.md`, `review.md`), the pull request and the review comment.

## What is where
```
architecture/views/      component view (+ state diagram), real sequence view (issue #3), stage map
architecture/decisions/  ADR-001 .. ADR-014 (Nygard); README.md = summary table, what the experiments changed
workflow/                orchestrator.py (state machine), agents.py (per-role tool policy), checks.py (deterministic checks),
                         prompts/, skills/requirements-spec (the A1 skill), review_seeded.py, exp1.py, copies of the workflow files, tests/
.github/workflows/       autose.yml, seeded-review.yml, exp1.yml (+ the upstream CI)
experiment/              issues/ (the 5 issues), hidden_tests/ (hashes now, files at the end), seeded_prs/, validation/, security/, variants.md, exp1/
results/                 results.csv, runs.md (every run, PR and review link, failures included), analysis.md, stage_pass_rates.md, per-experiment folders
ARCHITECTURE.md          the A2 architecture document the Design stage uses
```
Design: three agents (Planner stages 1-2, Builder 3-4, Reviewer 6; release is plain code), one deterministic Python orchestrator that decides every transition, deterministic checks that decide every pass or fail, least-privilege tools per role, a GitHub token that agents never see, and hard budgets (ADR-001 to ADR-010).

## Results in one paragraph
All five issues went from label to a tested, CI-green, reviewed PR (#10, #14, #15, #17, #26) for about $0.06 to $0.09 each; hidden tests pass 3/3, 3/3, 3/3, 4/4 and (vague issue) 5/6 (`results/analysis.md`). **11 attempts failed along the way and none was caused by the agents' capability** (10 were defects in my pipeline or setup, 1 was a deliberate budget test), which is why ADR-004 was superseded by ADR-011 and ADR-012/013 were written. Experiment 2 (independent Sonnet reviewer vs a Haiku reviewer that also sees the author's artifacts, 14 reviews each) gave a negative result for independence: 8/10 vs 10/10 defects caught, at $0.55 vs $0.05. The pre-registered test of the prompt change (ADR-014) was partly met and the change was **not adopted**. A prompt-injection issue and a budget-cap test were resisted/verified.

## Honest notes and limits
- **Experiment 1 (single agent vs three) was not run.** The API returned "Credit balance is too low" on 18 of 20 runs (run 45010442196); no result is reported from it, and ADR-001 is marked untested.
- **Cost:** the orchestrator tracked about $2.6 of spend, but the provider ran out of credit earlier than that; the console number is the authoritative one.
- **Issue #5's questions were answered by the assistant** on the maintainer's delegation (`1a, 2a, 3a`), not independently by the maintainer.
- **Hidden tests** are private while runs happen (agents read the repository). `experiment/hidden_tests/MANIFEST.sha256` holds their hashes from before the runs; the change log there records the one edit (issue 5, made before its ask-mode run was resumed).
- **Extra issues #28 (prompt injection) and #30 (pipeline tests: budget cap, fault injection)** are not among the five experiment issues and are excluded from pass-rate statistics. The runs with fault injection are labelled in `results/runs.md`.
- The seeded reviewer-check PRs (`experiment/seeded_prs/`) were written by me; two confounds in my own first designs were found and removed (the pilot is kept in `results/exp2_pilot_v1/`), and a tooling bug invalidated three reviews (kept and flagged).
- Setup and documentation pull requests of the fork were merged by the maintainer's side; **the AutoSE pull requests (#10, #14, #15, #17, #26, #31, #32) are left open**, and #18 (a baseline) was closed.

## AI use (disclosure)
Substantial help from Claude Code (Claude Sonnet 5.5): it wrote the workflow, the orchestrator, agents, checks, scripts, tests and experiment tooling, ran the experiments, and wrote the text of the ADRs, the views, the analysis and these notes. **The decisions are the author's:** the author's own answers in the design discussion decided D1 (three agents), D2 (a single Python orchestrator), D6 (Haiku for Planner and Builder, Sonnet for the Reviewer), the choice of experiments, the human gate for vague issues (ADR-013) and the spending limit; the other ADR decisions were proposed by the assistant and accepted by the author. Each ADR file has a "Decided by" line and `architecture/decisions/README.md` has a provenance section. *[Author to confirm this description before submission.]*

## Reproduce the scoring
`python experiment/validation/validate.py` (hidden-test validation), `python experiment/seeded_prs/build_v2.py` / `build_v3.py` (seeds), `python experiment/seeded_prs/score.py <results.jsonl>` (reviewer experiments), `python results/aggregate.py` (results.csv), `python -m pytest workflow/tests -c /dev/null` (30 tests of the checks, tool policy and rules). The hidden tests are in `experiment/hidden_tests/` once released.

## Still to do before submission
`report.pdf`, `demo.mp4`, the console figures for tokens and cost, the hidden tests copied into `experiment/hidden_tests/`, and the submission file `roll_number_a3_AutoSE.txt` (needs the roll number).
