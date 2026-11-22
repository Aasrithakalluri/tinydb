# A3 AutoSE — Progress Tracker

Reference: [assignment.md](assignment.md). Tick boxes (`[x]`) as we go.

> **Deadline note:** Due 21 Nov 23:59 IST; portal shows "Closed". Check whether an extension was requested/approved (max 3 days total across assignments, must be asked before deadline).

**Order of work:** Setup → Design (ADRs/views committed FIRST) → Build → Experiments → Results → Report/Video → Submit.

---

## Phase 0 — Decisions to make up front
- [ ] Pick target repo (tinydb `edff96a` / mistune `f7ec702` / structlog `19c4f21` / Python-Markdown `3f2c551` / other, tests < 5 min)
- [ ] Pick agent SDK/framework (Claude Agent SDK / OpenAI Agents SDK / LangGraph / mini-swe-agent)
- [ ] Pick model(s) per role (implementer vs reviewer)
- [ ] Pick which 8–10 ADRs (D1–D10) to write, and which **2 ADRs** to experimentally test
- [ ] Locate A1 skill (requirements) and A2 `ARCHITECTURE.md` for the chosen repo
- [ ] Set up a git repo in this folder and a GitHub account/org for the fork

## Phase 1 — Repository setup (Part 1)
- [ ] Fork the chosen repo (public) — record **fork URL**
- [ ] Pin to a specific commit — record **commit hash**
- [ ] Confirm test suite runs locally and in CI in < 5 min
- [ ] Add API keys as **repository secrets** (never in code/logs/prompts)
- [ ] **Set a hard spending limit** with the model provider (before first run)
- [ ] Protect `main` branch (no direct pushes)
- [ ] Create the label (e.g. `autose`)
- [ ] Write **5 issues** like real users: 
  - [ ] Bug report #1
  - [ ] Bug report #2
  - [ ] Feature request #1 (small)
  - [ ] Feature request #2 (small)
  - [ ] Vague issue
- [ ] Write **2–4 hidden acceptance tests per issue**, kept outside the repo (`experiment/hidden_tests/`)
- [ ] Save issue texts to `experiment/issues/`

## Phase 2 — Design before build (Part 2) — commit BEFORE any agent code
- [ ] Create repo skeleton (README, architecture/, workflow/, experiment/, results/)
- [ ] **Component view** (agents, tools, how they call each other) → `architecture/views/`
- [ ] **Sequence view** (placeholder now; fill from a *real* run later)
- [ ] **Stage map table** (agent / artifact / check per stage)
- [ ] Write ADRs in Nygard format (Context, Decision, Status, Consequences) in `architecture/decisions/` — at least 8 of:
  - [ ] D1 Splitting the work
  - [ ] D2 Control flow
  - [ ] D3 Hand-offs
  - [ ] D4 State
  - [ ] D5 Tools
  - [ ] D6 Models
  - [ ] D7 Checks
  - [ ] D8 Reviewer independence
  - [ ] D9 Safety and failures
  - [ ] D10 Triggers
- [ ] **Commit views + ADRs first** (git history must show design preceded agent code)
- [ ] Rule: wrong ADRs are marked *Superseded* (kept), plus a new ADR explaining what was learned

## Phase 3 — Build the workflow (Part 3)
- [ ] `.github/workflows/autose.yml` with triggers: `issues: labeled`, `issue_comment: created`
- [ ] Trigger auth: only maintainers/collaborators can start; ignore fork PRs / untrusted actors
- [ ] Concurrency control (two simultaneous runs on the same issue)
- [ ] Least-privilege `permissions:` per job
- [ ] Treat issue/comment text as **untrusted** (prompt-injection defenses, delimiting, no shell interpolation of issue text)
- [ ] **Stage 1 Requirements** → `spec.md`; check: all acceptance criteria testable
- [ ] **Stage 2 Design** → `design.md`; check: names files and functions to change
- [ ] **Stage 3 Implementation** → `diff.patch` on new branch; check: code builds
- [ ] **Stage 4 Testing** → `test_report.md`; check: new + existing tests all pass; loop back to stage 3 within budget
- [ ] **Stage 5 Release** → `pr.md` + PR link; check: PR open and CI passes
- [ ] **Stage 6 Review** (independent) → `review.md`; check: approve or 2 rounds used
  - [ ] Reviewer sees only: issue + diff + repo at PR head commit
  - [ ] Reviewer does NOT see implementer conversation/reasoning
  - [ ] Own prompt; read + run permission; **no push**
  - [ ] Anti-rubber-stamp mechanism (e.g. adversarial prompt, must-run-tests, different model)
- [ ] Back-edges: tests fail → stage 3 (or 2); review code issue → 3; approach issue → 2; max 2 review rounds
- [ ] Failing stage writes explanation in its artifact and stops the run
- [ ] Budgets/timeouts per stage and per run; token usage logged
- [ ] Workflow **never merges**; final decision left to human
- [ ] Run is followable on GitHub (artifacts uploaded, PR, review comment)
- [ ] Copy workflow + agent code + prompts into `workflow/`

## Phase 4 — Experiments
- [ ] Prepare **5 seeded PRs** for reviewer check (diffs + labels) → `experiment/seeded_prs/`
- [ ] Choose **2 ADRs to test**; define variants in `experiment/variants.md`
- [ ] Run each variant on the 5 issues (real runs only)
- [ ] Record every Actions run, PR, review link in `results/runs.md`
- [ ] Record metrics in `results/results.csv`
- [ ] Run hidden tests against each resulting PR
- [ ] Track total tokens used and cost
- [ ] Update design based on results (supersede ADRs where wrong; keep old ones)
- [ ] Capture one clean run for the sequence view and demo

## Phase 5 — Results analysis
- [ ] Pass rate per stage
- [ ] Hidden-test results per issue
- [ ] What the reviewer caught vs. where it was wrong (incl. seeded PRs)
- [ ] Side-by-side comparison of the 2 tested ADRs (negative results count equally)

## Phase 6 — Deliverables
- [ ] **report.pdf** (≤ 8 pages + appendices)
  - [ ] Architecture (2 pp): 3 views + which agent handles each stage
  - [ ] Design decisions (2.5 pp): summary table (decision, chosen, rejected, main reason, status) + discussion of top 3 decisions
  - [ ] Decision experiments (1.5 pp)
  - [ ] Results (1 pp)
  - [ ] Hindsight (0.5 pp)
  - [ ] Limitations & threats to validity (≥ 3)
- [ ] **Demo video** ≤ 5 min: full run from issue page to posted review (`demo.mp4` or link in README)
- [ ] **README.md**: fork URL + commit, models, how to trigger, **AI-use disclosure**
- [ ] Final repo layout matches the spec (see `assignment.md`)
- [ ] Fork is public (or TAs added as collaborators); every link in `runs.md` opens
- [ ] Verify no secrets in code/logs/prompts
- [ ] Verify workflow only touches our fork, never upstream; never merges
- [ ] Create `roll_number_a3_AutoSE.txt` containing **only** the GitHub repo link
- [ ] Submit

---

## Notes / Log
| Date | What was done | Links |
|------|---------------|-------|
|      |               |       |

## Key values (fill in as decided)
- Fork URL:
- Pinned commit:
- Agent framework:
- Models (implementer / reviewer):
- Spend limit set:
- Total tokens used:
