# A3 AutoSE — Progress Tracker

Reference: [assignment.md](assignment.md). `[x]` done and verified · `[~]` built, but not yet exercised by a real run (or only partly) · `[ ]` not started.

> **Deadline note:** original deadline 21 Nov 23:59 IST; an extension to 23 Nov was arranged by the author. Quality over speed: no compromises on evidence (decision made 2026-11-22).

## Where we are (snapshot, 2026-11-22, end of day)

**Phases 0 to 5 are done**: pipeline built and verified (both back-edges exercised through the orchestrator, fault-injected and labelled), all experiments run and written up, analysis and final checks done, README final. **Excluding the report and the video: 73 of 77 items (95%) are done.**

| Issue | Type | Outcome | PR | Cost | Hidden tests |
|-------|------|---------|----|------|--------------|
| #3 `count()` | feature | DONE, approved | [#10](https://github.com/Aasrithakalluri/tinydb/pull/10) | $0.058 | 3/3 |
| #1 `!=` vs `~(==)` | bug | DONE, approved | [#15](https://github.com/Aasrithakalluri/tinydb/pull/15) | $0.070 | 3/3 |
| #2 mutating search results | bug | DONE, approved (also rewrote the existing contract test) | [#14](https://github.com/Aasrithakalluri/tinydb/pull/14) | $0.086 | 3/3 |
| #4 `multiply` | feature | DONE after the lint fix | [#17](https://github.com/Aasrithakalluri/tinydb/pull/17) | $0.013 + $0.071 | 4/4 |
| #5 vague, auto | vague | DONE, baseline (PR closed) | [#18](https://github.com/Aasrithakalluri/tinydb/pull/18) | $0.019 + $0.163 | 5/6 (extra test) |
| #5 vague, ask | vague | DONE, approved (answers chosen by the assistant) | [#26](https://github.com/Aasrithakalluri/tinydb/pull/26) | $0.092 | 5/6 (extra test) |
| #28 injection test (extra) | security | attack resisted | [#31](https://github.com/Aasrithakalluri/tinydb/pull/31) | $0.075 | feature works |
| #30 pipeline tests (extra) | limits | budget cap, fault-injected tests and back-edges verified | [#32](https://github.com/Aasrithakalluri/tinydb/pull/32) | $0.016 + $0.082 + $0.128 | n/a |
| Experiment 1, 20 runs | experiment | all completed; first attempt invalid (my driver bug, $0.422) | – | $0.320 | 10/10 (3 agents) vs 9/10 (1 agent) excl. extra |

Spend (orchestrator-tracked, approximate): **about $3.4 of the $5 cap**; the Anthropic console is authoritative.

**Left, and only the maintainer can do it** (besides the report and the video): read the real spend and tokens from the console; read the 14 ADRs and confirm (then each gets a "Reviewed by the author" line); the roll number for `roll_number_a3_AutoSE.txt`; Submit. Optional: decide an escalation policy (would become ADR-015).

---

## Phase 0 — Decisions
- [x] Target repo: tinydb `edff96a`
- [x] Agent SDK: Claude Agent SDK, single Python orchestrator (ADR-002)
- [x] Models: Haiku for Planner and Builder, Sonnet for Reviewer (ADR-006)
- [x] ADRs written: all ten (D1–D10) plus ADR-011, 012, 013; tested ADRs chosen (see Phase 4)
- [x] A1 skill and A2 `ARCHITECTURE.md` located and in the repo
- [x] Git repo + GitHub fork (`Aasrithakalluri/tinydb`)

## Phase 1 — Repository setup
- [x] Fork, pinned to `edff96aeb2616402e9489d46e90a592c05565621` (default branch `master`)
- [x] Test suite runs in under a second locally (228 tests); CI runs on GitHub
- [x] `ANTHROPIC_API_KEY` stored as a repository secret
- [x] Hard spend limit of $5 set with the provider
- [x] `master` protected (direct push rejected, verified); changes via PR
- [x] `autose` label created
- [x] 5 issues opened (2 bugs, 2 features, 1 vague) — #1 … #5
- [x] Hidden acceptance tests (3–4 per issue) written, kept outside the repo in `~/a3_private/hidden_tests/`; **they fail on the baseline** (verified)
- [x] Issue texts saved to `experiment/issues/`
- [x] Hidden-test integrity: SHA-256 manifest in `experiment/hidden_tests/` (tests stay private while agents run)
- [x] Hidden tests copied into `experiment/hidden_tests/` after the last agent run on issues 1-5; manifest matches

## Phase 2 — Design before build
- [x] Component view, sequence view (planned), stage map → `architecture/views/`
- [x] ADR-001 … ADR-010 (Nygard format) → `architecture/decisions/`
- [x] Design committed before any agent code (PR #7 merged before PR #8 with the code)
- [x] ADRs written from the author's own interview answers (2026-11-22): reasons for ADR-001 to 010 and 013, lessons of 011, 012, 014, view on Exp 2; each ADR has "Decided by" and the author's reasons
- [x] Superseded-rule used: ADR-004 → superseded by ADR-011 (found by a real run); ADR-012 refines ADR-007/ADR-002; ADR-013 supersedes ADR-012's vague-issue rule
- [x] Sequence view replaced by one drawn from the real run on #3
- [x] Component view updated with the ask gate and a full state diagram

## Phase 3 — Build the workflow
- [x] `.github/workflows/autose.yml` (labeled + `/autose` comment triggers); lint clean with actionlint
- [x] Orchestrator state machine, per-role tool policy, deterministic checks, prompts → `workflow/`
- [x] Stages 1–6 all executed for real, with artifacts spec/design/diff/test_report/pr/review
- [x] Restart restores state **and code**; reuses the open PR (ADR-011)
- [x] Failing stage explains itself in its artifact and stops (exercised on #4 and #5)
- [x] Workflow never merges; humans merge
- [x] Run followable: status comment, artifacts, PR, review comment
- [x] Unit tests for the checks → `workflow/tests/test_checks.py` (5 pass)
- [x] Ask-the-human gate (`/autose ask` → WAITING → `/autose go ...`), ADR-013; first real pause worked
- [x] Trigger authorization: real permissions API refuses an outsider (`octocat`) and accepts the owner; unit-tested (checked locally, not inside Actions)
- [x] Tool policy tested (23 tests in `workflow/tests/`): read-only planner, builder writes only `tinydb/`+`tests/`, Bash allowlist rejects curl/git push/env/chaining/gh
- [x] Denied tool calls recorded in `state.json` with what and why
- [x] Concurrency verified for real: a second trigger during an active run stayed `pending` until the first finished
- [x] Back-edge TEST → IMPLEMENT exercised for real (fault-injected, labelled); finding: Builder grew the diff 18 → 201 lines "fixing" a failure that did not exist
- [x] Agent-level timeout unit-tested (31 workflow tests pass)
- [x] Reviewer "changes" and redesign back-edges exercised through the orchestrator (fault-injected, labelled; run 45021250106, $0.128)
- [x] Budget cap verified (cap $0.02 → stopped before the reviewer); gap found and fixed: PR notice when a run stops early
- [x] Anti-rubber-stamp rule unit-tested (approve without a pytest run, or garbage JSON, is overruled)
- [x] Anti-rubber-stamp in practice: measured on the seeded PRs; the rule never fired (every review ran the suite), so the protection came from the prompt and the model
- [x] Prompt injection: real attack issue #28 resisted at every stage (`experiment/security/results.md`); one direct attack only
- [x] Allowlist widened narrowly for `2>&1 | tail N` (benign friction), 30 workflow tests
- [x] Reviewer reads ARCHITECTURE.md: after the prompt fix all 7 checked reviews cite the constraints (3–5 mentions each)

## Phase 4 — Experiments
- [x] Variants defined in `experiment/variants.md`: Exp 1 = ADR-001 (3 agents vs 1 for stages 1–4), Exp 2 = ADR-008 (independent Sonnet reviewer vs Haiku reviewer that sees implementer artifacts), Exp 3 = ADR-013 (assume vs ask, issue #5 only)
- [x] Baseline (variant A) run once on every issue
- [x] Hidden tests run against every finished PR (#10, #15, #14, #17, #18)
- [x] Every run logged in `results/runs.md` (needs rows for the later runs: #4 and #5 reruns, ask-mode run)
- [x] Ask-mode run on #5 finished (PR #26, $0.092, hidden 5/6 = same as auto; answers chosen by the assistant on delegation)
- [x] Exp 1 tooling built and tested offline (single-agent mode, stop after stage 4, budgeted driver `workflow/exp1.py`, local scorer `experiment/exp1/score.py`)
- [x] Exp 2 variants implemented (`workflow/review_seeded.py`, variant A Sonnet independent / B Haiku with the author's artifacts; scorer `experiment/seeded_prs/score.py`; workflow `seeded-review.yml`), tested offline
- [x] 7 seeded PRs built and verified (S1–S5 defective, C1–C2 correct): suite green on all, hidden tests fail on defective / pass on controls; branches `seeded/*` pushed
- [x] Exp 2 pilot (seeds v1) run and read: A caught 8/10 (missed S4 twice), B 10/10 but 2/4 false rejections; **confound found** (B's artifacts described different code) → seeds v2 built from the real PRs with one injected defect (suite green, hidden tests fail); pilot kept in `results/exp2_pilot_v1/`
- [x] Exp 2 on seeds v2 (both variants, 2 runs each) scored and read: A (independent Sonnet) 8/10 caught (missed S4 twice), B (Haiku + author's artifacts) 10/10, 0 false rejections each; A $0.551 vs B $0.046. Hypothesis NOT supported. A tooling bug invalidated S3 in the first dispatch (stale branch) → re-run + runner guard. → ADR-014 (Proposed)
- [x] New seeds built and verified (S6 hash tag copied from a sibling, S7 unrequested reversal of the documented remove(doc_ids) rule with 3 pinning tests rewritten, C3 control); reviewer prompt v2 written (`reviewer_v2.md`, variant A2); success criterion pre-registered in `experiment/seeded_prs/v3/PREREGISTRATION.md` before any run
- [x] ADR-014 test run and the pre-registered rule applied: A2 caught S4/S6/S7 6/6 and labelled S7 `approach`, but rejected the correct control C2 twice → ADR-014 stays **Proposed**, production prompt unchanged. The old prompt already caught S6/S7 (seeds do not discriminate); steps 6 and 7 are confounded. 18 reviews, $0.733 (`results/adr014_test/`)
- [x] Reviewer-"changes" and redesign back-edges exercised (run 45021250106, $0.128, DONE after a second review)
- [x] Exp 1 run and scored (`results/exp1/`): 20 runs, all completed; hidden tests 10/10 (3 agents) vs 9/10 (1 agent) excl. extra; $0.0202 vs $0.0118 per run; the one difference is a deliberate non-fix of issue #2 reported DONE; no design change. First attempt invalid (my driver bug), logged.
- [x] Hidden tests validated with a reference + alternative fix per issue (`experiment/validation/`); finding: issue #2 conflicts with a documented contract and an existing test
- [x] `results/results.csv` (from final states, `results/aggregate.py`)
- [ ] Total tokens and cost from the Anthropic console (maintainer reads it at the end)
- [x] Design updated from results: `architecture/decisions/README.md` (summary table of all 14 ADRs, what each experiment changed, notes on the top 3 decisions); ADR-001 untested, ADR-009 addendum
- [x] Clean run for the sequence view (#3) and the demo (walk through the finished run on #1, no new spend)

## Phase 5 — Results analysis
- [x] Pass rate per stage, retries and pipeline-caused failures separately (`results/stage_pass_rates.md`): 5/5, 4/5, 5/5, 5/5, 5/5, 5/5 first try; 11 failed attempts, none caused by agent capability
- [x] Hidden-test results per issue and per variant (`results/analysis.md`, `results/exp1/results.csv`)
- [x] What the reviewer caught and where it was wrong (`results/analysis.md`)
- [x] Side-by-side comparison of the tested ADRs (Exp 1, Exp 2, ADR-014, ADR-013) in `results/analysis.md`

## Phase 6 — Deliverables
- [x] Report inputs settled (drafts adopted by the author: top-3 decisions, ADR-001 and ADR-008 side by side; tracked cost with a caveat; roll number 2025204019); Hindsight written in report_v2.pdf at the author's request
- [x] **report.pdf** written: 7 pages (5 body + 2 appendix), diagrams from the real artifacts, ADR table, two experiments side by side, results, 10 limitations, AI-use appendix; source `report/report.html`; **report_v2.pdf** (8 pages in total, the limit; Design decisions section expanded to 2.3 pages after verification found it thin and found an overclaim, now fixed) adds the three views labelled explicitly (View 1 component, View 2 sequence, View 3 stage map), Section 5 Hindsight (ADR-004 first, drafted from the evidence at the author's request) and Appendix F, a requirements checklist; `report.pdf` is unchanged
- [ ] **Demo video** ≤ 5 min: one full run from the issue page to the posted review
- [x] **README.md** final (fork, commit, models, triggers, layout, results, honest limits, AI-use disclosure; the author must confirm and rewrite the ADRs in their own words)
- [x] Repo layout matches the spec (only report.pdf and demo.mp4 missing; hidden tests copied at the end)
- [x] Fork is public; all 39 links in the results docs resolve
- [x] No secrets: working tree, full git history and 29 workflow logs scanned, 0 matches
- [x] Only our fork touched (0 upstream issues/PRs by us), no merge call in the code, AutoSE PRs left open, least-privilege permissions
- [x] All 14 ADRs read and adopted by Aasritha Kalluri on 2026-11-22 (first person, her as author, her reasons, "Reviewed and adopted by" line); inaccurate statements corrected while reading
- [x] `2025204019_a3_AutoSE.txt` created (contains only the GitHub link)
- [ ] Submit

---

## Findings so far (raw material for the report)
1. **Invalid workflow YAML** (`runner` context in job `env`): found only on push, fixed with actionlint.
2. **Repo setting** "Allow GitHub Actions to create pull requests" had to be enabled.
3. **Restart bug (ADR-004 → ADR-011):** restoring `state.json` did not restore code; an empty commit was force-pushed and PR #10 briefly had 0 changes. A reasoned ADR was falsified by one real run.
4. **CI wait matched a gated `pull_request` run** (`action_required`); fixed to use the `workflow_dispatch` run.
5. **Lint false rejection (ADR-012):** tagged criteria such as `FR-03-AC1 (failure):` were invisible to my regex, so a correct spec for #4 failed stage 1.
6. **Vague issue:** with no human available, the Planner wrote "do not implement until Q-01 is resolved" and the Builder produced an empty diff. Led to assume-mode (ADR-012) and ask-mode (ADR-013).
7. **Assume-mode guess approved by the reviewer** (#5): the reviewer does not see the spec, so it cannot challenge an ASSUMED interpretation. Hidden tests 2/3.
8. **Design lint caught a real error:** the Planner named a test symbol that did not exist (#3, #5); the retry fixed it.
9. **Reviewer quality signals:** it ran the suite and its own experiments, checked constraints 4 and 5, and for #2 noticed that the ADR-3 wording in `ARCHITECTURE.md` is now stale.
11. **Wrong artifact restored** (API lists by id, not time) and **red master CI** (`pytest` collected workflow tests): both fixed, ADR-011 addenda.
12. **Ask vs assume (#5):** same score (5/6), asking cheaper ($0.092 vs $0.163); null result, answers chosen by the assistant.
13. **Prompt injection resisted** (one direct attack); denied calls were benign formatting.
14. **Budget cap left an unreviewed PR looking finished** → PR notice added. **A fake failure made the Builder inflate the diff** 18 → 201 lines.
15. **Issue #2 asks to break a documented, tested contract** (`Table.search` docstring + `test_query_cache_documents_are_shared_with_cache`); the pipeline rewrote that test, the reviewer approved; any valid fix must change it. 1 of 8 PRs removed assertions from existing tests.
16. **My tooling hid its own failure:** a stale local branch was pushed instead of the new seed commit and the build output filtered the error, so S3 was reviewed against the wrong defect; fixed with an explicit HEAD push, visible errors and a runner guard comparing each branch diff with its patch. Invalid reviews kept and flagged.
17. **Two confounds in my own experiment design** (variant B given artifacts of different code; v2 mutations that made the PR's own suite fail) found and removed before the main result; pilot kept.
18. **ADR-014 result:** the compare-with-siblings prompt fixed S4 and routed the contract reversal (S7) to `approach`, but falsely rejected a correct control; the old prompt already caught the new seeds, so they did not discriminate. Stays Proposed (pre-registered rule).
19. **API credit ran out earlier than our tracker predicted** ("Credit balance is too low" on 18 of 20 Exp 1 runs); either the credit was below $5 or our estimate undercounts. The console is authoritative; no result invented.
20. **Exp 1:** single agent vs three agents: no quality difference attributable to the split, the split costs about 70% more per run; the single agent's one failure was a deliberate non-fix of the contract-conflict issue that the pipeline reported as DONE (checks do not require a listed change to be applied; xfail hides it).
21. **Two of my own tool bugs in one experiment** (artifacts inside the repo; relative patch path in the scorer) cost $0.42 and a wrong 0/0; both fixed and guarded.
10. **Cost is small:** ≈ $0.06–0.09 per clean run; the vague issue costs 2–3× more.

## Notes / Log
| Date | What was done | Links |
|------|---------------|-------|
| 2026-11-22 | Phases 1–3 done; first complete run on #3 after 3 pipeline fixes (ADR-011) | PR #10 |
| 2026-11-22 | Batch on #1, #2, #4, #5: two successes, two pipeline-caused failures; fixes in ADR-012 | PR #14, #15 |
| 2026-11-22 | #4 and #5 re-run; ADR-013 ask gate built; #5 baseline (auto) saved to `results/variant_runs/issue5-auto/`; ask-mode paused waiting for the maintainer | PR #17, #18, run 44997454477 |

## Key values
- Fork URL: https://github.com/Aasrithakalluri/tinydb
- Pinned commit: edff96aeb2616402e9489d46e90a592c05565621 (default branch `master`)
- Agent framework: Claude Agent SDK 0.2.187, single Python orchestrator (`workflow/orchestrator.py`)
- Models: Planner/Builder `claude-haiku-5-5`, Reviewer `claude-sonnet-5-5`
- Spend limit: $5 (Anthropic); orchestrator cap $0.60 per run
- Total tokens used so far: ≈ 3.8M in / 270k out (orchestrator-tracked; confirm in the console)
