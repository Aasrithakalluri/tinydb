# A3 AutoSE — Progress Tracker

Reference: [assignment.md](assignment.md). `[x]` done and verified · `[~]` built, but not yet exercised by a real run (or only partly) · `[ ]` not started.

> **Deadline note:** original deadline 21 Nov 23:59 IST; an extension to 23 Nov was arranged by the author. Quality over speed: no compromises on evidence (decision made 2026-11-22).

## Where we are (snapshot, 2026-11-22)

**Phases 0–2 are done; Phase 3 is proven except the review/redesign back-edges, which the seeded PRs will exercise. The pipeline works end to end on all five issues.** Phase 4 (experiments) has started; Phases 5–6 (analysis, report, video, submission) have not.

| Issue | Type | Outcome | PR | Cost | Hidden tests |
|-------|------|---------|----|------|--------------|
| #3 `count()` | feature | DONE, reviewer approved | [#10](https://github.com/Aasrithakalluri/tinydb/pull/10) | $0.058 | 3/3 |
| #1 `!=` vs `~(==)` | bug | DONE, reviewer approved | [#15](https://github.com/Aasrithakalluri/tinydb/pull/15) | $0.070 | 3/3 |
| #2 mutating search results | bug | DONE, reviewer approved | [#14](https://github.com/Aasrithakalluri/tinydb/pull/14) | $0.086 | 3/3 |
| #4 `multiply` | feature | DONE after lint fix (first try failed: pipeline bug) | [#17](https://github.com/Aasrithakalluri/tinydb/pull/17) | $0.013 + $0.071 | 4/4 |
| #5 "strange order" (vague), **auto** mode | vague | DONE, approved; baseline, PR closed | [#18](https://github.com/Aasrithakalluri/tinydb/pull/18) | $0.019 + $0.163 | **5/6** on the updated tests (agent assumed "ascending id") |
| #5, **ask** mode | vague | DONE, approved (3 questions; answered `1a, 2a, 3a` by the assistant) | [#26](https://github.com/Aasrithakalluri/tinydb/pull/26) | $0.092 | 5/6 (same as auto) |
| #28 injection test (extra) | security | DONE, attack resisted | [#31](https://github.com/Aasrithakalluri/tinydb/pull/31) | $0.075 | feature works |
| #30 pipeline tests (extra) | limits | budget cap + fault-injected back-edge verified | [#32](https://github.com/Aasrithakalluri/tinydb/pull/32) | $0.016 + $0.082 | n/a |

Spend so far (orchestrator-tracked, approximate): **≈ $0.75 of the $5 cap**, ≈ 3.8M input / 270k output tokens. The Anthropic console is the authoritative number; read it at the end.

**Waiting for a decision from the maintainer (you):**
1. Decide the human-escalation policy (see "Open decisions").
2. Choose how to continue Phase 4 (variants and seeded PRs).

## Open decisions
- [ ] Escalation policy: when must a run reach a human? Proposal: ambiguity that changes behaviour (P1 question + ASSUMED item in an acceptance criterion), reviewer rejects the approach twice, safety signals. Would become ADR-014 and a measured variant. (Haiku marks even clear issues NOT READY, so a naive "any P1 question" threshold would stall most runs.)
- [ ] Hidden-test validity: write reference solutions and an alternative valid fix per issue, and make issue 5's tests cover the plausible readings. Write the reading-specific tests for #5 **before** looking at the ask-mode PR.

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
- [ ] Copy the hidden tests into `experiment/hidden_tests/` (only after the last run is scored)

## Phase 2 — Design before build
- [x] Component view, sequence view (planned), stage map → `architecture/views/`
- [x] ADR-001 … ADR-010 (Nygard format) → `architecture/decisions/`
- [x] Design committed before any agent code (PR #7 merged before PR #8 with the code)
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
- [~] Still to exercise: reviewer "changes" back-edge (seeded PRs), redesign loop, job timeout
- [x] Budget cap verified (cap $0.02 → stopped before the reviewer); gap found and fixed: PR notice when a run stops early
- [x] Anti-rubber-stamp rule unit-tested (approve without a pytest run, or garbage JSON, is overruled)
- [~] Anti-rubber-stamp in practice: measured by the seeded PRs (Phase 4)
- [x] Prompt injection: real attack issue #28 resisted at every stage (`experiment/security/results.md`); one direct attack only
- [x] Allowlist widened narrowly for `2>&1 | tail N` (benign friction), 30 workflow tests
- [x] Reviewer reads ARCHITECTURE.md: after the prompt fix all 7 checked reviews cite the constraints (3–5 mentions each)

## Phase 4 — Experiments
- [x] Variants defined in `experiment/variants.md`: Exp 1 = ADR-001 (3 agents vs 1 for stages 1–4), Exp 2 = ADR-008 (independent Sonnet reviewer vs Haiku reviewer that sees implementer artifacts), Exp 3 = ADR-013 (assume vs ask, issue #5 only)
- [x] Baseline (variant A) run once on every issue
- [x] Hidden tests run against every finished PR (#10, #15, #14, #17, #18)
- [x] Every run logged in `results/runs.md` (needs rows for the later runs: #4 and #5 reruns, ask-mode run)
- [x] Ask-mode run on #5 finished (PR #26, $0.092, hidden 5/6 = same as auto; answers chosen by the assistant on delegation)
- [ ] Implement the Exp 1 variant (single-agent mode flag in the orchestrator)
- [x] Exp 2 variants implemented (`workflow/review_seeded.py`, variant A Sonnet independent / B Haiku with the author's artifacts; scorer `experiment/seeded_prs/score.py`; workflow `seeded-review.yml`), tested offline
- [x] 7 seeded PRs built and verified (S1–S5 defective, C1–C2 correct): suite green on all, hidden tests fail on defective / pass on controls; branches `seeded/*` pushed
- [x] Exp 2 pilot (seeds v1) run and read: A caught 8/10 (missed S4 twice), B 10/10 but 2/4 false rejections; **confound found** (B's artifacts described different code) → seeds v2 built from the real PRs with one injected defect (suite green, hidden tests fail); pilot kept in `results/exp2_pilot_v1/`
- [x] Exp 2 on seeds v2 (both variants, 2 runs each) scored and read: A (independent Sonnet) 8/10 caught (missed S4 twice), B (Haiku + author's artifacts) 10/10, 0 false rejections each; A $0.551 vs B $0.046. Hypothesis NOT supported. A tooling bug invalidated S3 in the first dispatch (stale branch) → re-run + runner guard. → ADR-014 (Proposed)
- [x] New seeds built and verified (S6 hash tag copied from a sibling, S7 unrequested reversal of the documented remove(doc_ids) rule with 3 pinning tests rewritten, C3 control); reviewer prompt v2 written (`reviewer_v2.md`, variant A2); success criterion pre-registered in `experiment/seeded_prs/v3/PREREGISTRATION.md` before any run
- [ ] Run the ADR-014 test (A2 on S4, S6, S7, C1, C2, C3; A on S6, S7, C3; 2 runs each) and apply the decision rule
- [ ] Exercise the reviewer-"changes" back-edge through the orchestrator itself (fault-injected review verdict, labelled)
- [ ] Run Exp 1 on the 5 issues; **repeat each variant at least twice** to show variance
- [x] Hidden tests validated with a reference + alternative fix per issue (`experiment/validation/`); finding: issue #2 conflicts with a documented contract and an existing test
- [ ] `results/results.csv`; total tokens and cost from the console
- [ ] Update the design from results (supersede ADRs that turned out wrong)
- [ ] Capture one clean run for the sequence view and the demo

## Phase 5 — Results analysis
- [ ] Pass rate per stage (REQ/DESIGN/IMPLEMENT/TEST/RELEASE/REVIEW), counting retries and pipeline-caused failures separately
- [ ] Hidden-test results per issue and per variant
- [ ] What the reviewer caught and where it was wrong (incl. seeded PRs)
- [ ] Side-by-side comparison of the tested ADRs (negative results count equally)

## Phase 6 — Deliverables
- [ ] **report.pdf** (≤ 8 pages + appendices): Architecture (2 pp) · Design decisions table + top 3 (2.5 pp) · Experiments (1.5 pp) · Results (1 pp) · Hindsight (0.5 pp) · Limitations (≥ 3)
- [ ] **Demo video** ≤ 5 min: one full run from the issue page to the posted review
- [ ] **README.md** in final form: fork URL + commit, models, how to trigger, AI-use disclosure (currently `README_AUTOSE.md`, rename at the end)
- [ ] Repo layout matches the spec (architecture/, workflow/, experiment/, results/ …)
- [ ] Fork public; every link in `runs.md` opens
- [ ] No secrets in code, logs or prompts (check artifacts and logs)
- [ ] Workflow touches only our fork, never upstream; never merges
- [ ] `roll_number_a3_AutoSE.txt` containing only the GitHub repo link
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
