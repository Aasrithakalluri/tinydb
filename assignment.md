# Assignment 3 — Architecting an Agentic SDLC Workflow

Build a GitHub Actions workflow in which agents turn an issue into a tested and reviewed pull request, and explain the reasoning behind its design.

**Due:** 21st November 23:59 IST (status shown: Closed, deadline passed)
**Released:** Friday 13th November
**Extension policy:** 3 days in total across all assignments, only if asked before the deadline.

---

## Issue In, Pull Request Out

You will build a GitHub Actions workflow that takes an issue and produces a pull request. A maintainer starts the workflow by adding a label to an issue or by posting a comment. From there, a set of agents writes the spec and the design, changes the code, tests it, opens a pull request, and has it checked by a separate reviewer agent.

Most of the marks are for your **architecture**: how you divide work between agents, how agents pass work to each other, and why you chose this design.

**The story so far.**
- A1: you built an agent skill that turns a vague idea into a specification.
- A2: you tested whether architecture documentation helps an agent change code written by someone else.
- Now: maintainers want to add a label to an issue and later find a tested and reviewed pull request waiting for them. Before they allow a bot into their repository, they want to understand how it is designed and why.

## Your Mission

The workflow should be in `.github/workflows/`. Sketch of the trigger:

```yaml
# .github/workflows/autose.yml  (a sketch, not a template)
on:
  issues:
    types: [labeled]        # e.g. a maintainer adds the label "autose"
  issue_comment:
    types: [created]        # e.g. "/autose" on an issue or an open PR
permissions:
  contents: write
  pull-requests: write
  issues: write
jobs:
  # your design: one job or several, one agent or many, chained how you choose
```

After the workflow starts, it should go through the six stages below. The stages are fixed, but you decide how your agents carry them out. Each stage saves its output as an artifact. A stage hands over to the next one only after its check has passed.

| # | Stage | What the agent does | Artifact | Check before moving on |
|---|-------|---------------------|----------|------------------------|
| 1 | Requirements | Writes a spec with acceptance criteria from the issue. Reuse your A1 skill. | `spec.md` | All acceptance criteria are testable. |
| 2 | Design | Plans the change and lists the files to edit. Use your A2 `ARCHITECTURE.md`. | `design.md` | The plan names the files and functions to change. |
| 3 | Implementation | Changes the code on a new branch, following the design. | `diff.patch` | The code builds. |
| 4 | Testing | Writes a test for each acceptance criterion and runs the full test suite. Goes back to stage 3 if tests fail. | `test_report.md` | All new and existing tests pass. |
| 5 | Release | Pushes the branch and opens a pull request. | `pr.md` + PR link | The pull request is open and CI passes. |
| 6 | Review | A separate reviewer agent reviews the pull request. Requested changes go back to the stage that needs fixing, at most twice. | `review.md` | The reviewer approves, or two review rounds are used up. |

If a stage cannot pass its check, it should explain why in its artifact and stop the run. A stage can also send work back to an earlier stage when needed. For example, if tests keep failing, the design may need to change; if the reviewer disagrees with the approach, the workflow should return to the design stage.

### Keeping the reviewer independent

- The reviewer should only see the **issue, the diff, and the repository at the latest commit of the PR**. It can run the code itself.
- It must **not** see the implementer's conversation or reasoning.
- Give it its own prompt and permission to **read and run code, but not to push**.
- You may use a different model for the reviewer (not required).
- In your report, explain how you make sure the reviewer does not simply agree with the implementer.

## The Heart of It: Your Architecture and Why

A workflow that only partly works but comes with a clear, evidence-based explanation of its design is preferred over one that works but cannot explain why it is built that way. One agent or many, a fixed pipeline or a planner — as long as you can explain your choice.

Reference design (flow): Requirements → Design → Implement → Test (tests fail: retry within budget) → Release (open PR, CI) → Independent review (fresh context, no push) → Human decides merge or close. Review sends *code issue* back to Implement and *approach issue* back to Design; max 2 review rounds.

Whatever design you choose, it **must**:
- keep the six stages and their checks,
- use a reviewer that is independent of the other agents,
- leave the final merge decision to a person.

## Decisions to Justify

Write an ADR for **at least 8 of the following 10** decisions. Questions below are the bare minimum; go beyond them.

| # | Decision | Questions to answer |
|---|----------|---------------------|
| D1 | Splitting the work | How many agents, and which stages does each handle? Why better than one agent for everything or one agent per stage? |
| D2 | Control flow | Fixed pipeline, orchestrator with workers, state machine, or separate Actions jobs that trigger each other? Who decides when to go back to an earlier stage? |
| D3 | Hand-offs | What does each agent receive (full artifacts, summaries, repo access)? What do you deliberately leave out, and why? |
| D4 | State | Where is information stored between stages and between runs (files on branch, PR comments, workflow artifacts, cache)? What happens if a run is restarted? |
| D5 | Tools | Which tools does each agent have, and how are they provided (MCP server, `gh` CLI, REST API)? How do you make sure each agent can only do what it needs to? |
| D6 | Models | Which model for each role, and why? Consider ability, cost, speed, and the value of using different models. |
| D7 | Checks | How is each stage's check carried out (tests, static analysis, LLM judge, or a mix)? Who makes the final pass/fail decision? |
| D8 | Reviewer independence | How do you keep the reviewer separate (own job, model, prompt, permissions)? How do you stop it from approving everything? |
| D9 | Safety and failures | How do you handle budgets, timeouts, GitHub Actions limits, stuck stages? Since anyone can write an issue, how do you protect against prompt injection? |
| D10 | Triggers | Which events start the workflow, and who is allowed to start it? What happens if two runs start at the same time? |

**ADR format:** Nygard format from A2.

**Architecture views** (along with the ADRs):
1. A **component view** showing the agents, their tools and how they call each other.
2. A **sequence view** showing one *real* run from the trigger to the review.
3. A **table** listing the agent, artifact and check for each stage.

## What to Do

### Part 1: Set Up Your Repository
1. Fork a repository, pin it to a specific commit and write down the commit hash. Options from A2: tinydb `edff96a`, mistune `f7ec702`, structlog `19c4f21`, Python-Markdown `3f2c551` — or any repo whose tests run in under five minutes.
2. Open **five issues** in your fork, written the way real users would: **2 bug reports, 2 small feature requests, 1 vague**. For each, write **2–4 hidden acceptance tests** and keep them outside the repository (as in A2).
3. Store model API keys as **repository secrets**, and **protect the main branch** so nobody can push to it directly.

### Part 2: Design Before You Build
Commit your component view and your first ADRs **before** writing any agent code, so git history shows design came first. If a run shows one of your ADRs was wrong, leave the old ADR in place and mark it **Superseded**, then add a new ADR explaining what you learned.

### Part 3: Build the Workflow
- Write the workflow and the agent code it calls. Any SDK/framework is fine: Claude Agent SDK, OpenAI Agents SDK, LangGraph, mini-swe-agent. A ready-made "fix this issue" action may be used as one step, as long as the design around it and its ADR are your own.
- Give each job only the permissions it needs; treat issue and comment text as **untrusted input**.
- Make sure anyone can follow a run on GitHub via its artifacts, the pull request and the review.

## What to Submit

### Report (`report.pdf`, at most 8 pages plus appendices)
- **Architecture (2 pages):** your three views, and which agent handles each stage.
- **Design decisions (2.5 pages):** a table summarising all ADRs — decision, option chosen, main option rejected, main reason, status. Then discuss the three decisions that mattered most. Full ADRs go in `decisions/`.
- **Decision experiments (1.5 pages):** the two ADRs you tested, results side by side, and what you changed as a result.
- **Results (1 page):** pass rate per stage, hidden-test results, what the reviewer caught and where it was wrong.
- **Hindsight (half a page):** if starting again tomorrow, which decision would you change first, and why?
- **Limitations and threats to validity** (at least three).

### Demo video (at most 5 minutes)
One complete run, from the issue page to the posted review. Brownie points for engaging and insightful videos.

### Submission
Submit a file named `roll_number_a3_AutoSE.txt` containing **only the GitHub link to your repository**.

### Repository layout

```
README.md            # fork URL + commit, models, how to trigger the workflow
report.pdf
demo.mp4             # or a link in README.md
architecture/
  views/             # component view, sequence view, stage map
  decisions/         # ADR-001.md ... one per decision, superseded ones kept
workflow/            # copy of .github/workflows/ and all agent code + prompts
experiment/
  issues/            # the 5 issue texts
  hidden_tests/
  seeded_prs/        # the 5 reviewer-check PRs (diffs + labels)
  variants.md        # what each decision-experiment variant changes
results/
  results.csv
  runs.md            # links to every Actions run, PR and review
```

Keep your fork **public** until grades are released, or add the TAs as collaborators, so they can open every link in `runs.md`.

**Experiments that give negative results earn as many marks as those that give positive results.**

## Rules
- **Your fork only.** The workflow may push, comment and open PRs only in repositories your team owns, never in the original upstream project.
- **Never merge.** The workflow ends after the review; a person decides whether to merge.
- **Secrets.** Keep API keys in repository secrets, never in code, logs or prompts. Workflows triggered from forks do not receive secrets.
- **Cost.** Set a hard spending limit with your model provider before your first run, and report the total number of tokens used.
- **AI use.** Coding agents may help build the workflow. Per course policy, mention any substantial AI help in your README and review everything generated. **The ADRs and the reasoning behind them must be your own.**
- **Honesty.** All runs, PRs and results must be real and linkable. A fabricated run receives zero marks.

## Resources
- Lecture 6, Agentic Architecting, and your A2 ADR format
- AutoSE coding-agent pattern repository (Lecture 8)
- Anthropic, *Harness Design for Long-running Application Development* (Lecture 7)
- Yao et al., *ReAct* (Lecture 7)
- mini-swe-agent and SWE-bench (Lecture 9)
- SE Radio EP 730, *Harness Engineering for AI Agents* (Lecture 9)
- GitHub Actions docs (events that trigger workflows, `GITHUB_TOKEN` permissions)
- GitHub MCP server and the GitHub CLI

## One Last Thing…
Connecting a model to a button that opens pull requests is easy. The real engineering lies in deciding what each agent knows, what it is allowed to do, and who checks its work. Show us the choices you made, and show us that you understand why you made them.
