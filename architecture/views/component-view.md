# Component view

```mermaid
flowchart LR
    H([Maintainer]) -- "label autose / comment /autose" --> GH[(GitHub issue)]
    GH -- "issues:labeled / issue_comment:created" --> WF["autose.yml<br/>(one job, concurrency per issue)"]
    WF --> ORCH

    subgraph ORCH["orchestrator.py  (state machine, plain Python, holds GITHUB_TOKEN)"]
      direction TB
      CHK["Checks (deterministic)<br/>spec lint, design lint,<br/>compileall/import, pytest"]
      GIT["Release code<br/>git push + gh pr create<br/>(stage 5, no LLM)"]
      STATE[("state.json + stage artifacts<br/>spec.md design.md diff.patch<br/>test_report.md pr.md review.md")]
    end

    ORCH -- "issue text + ARCHITECTURE.md<br/>(untrusted-wrapped)" --> PL
    ORCH -- "design.md + acceptance criteria" --> BL
    ORCH -- "issue + diff, PR head SHA checkout" --> RV

    PL["Planner agent<br/>Haiku, stages 1-2<br/>tools: Read Grep Glob<br/>skill: requirements-spec"]
    BL["Builder agent<br/>Haiku, stages 3-4<br/>tools: Read Edit Write,<br/>Bash allowlist (pytest, python)"]
    RV["Reviewer agent<br/>Sonnet, stage 6<br/>tools: Read Grep Glob,<br/>Bash allowlist (pytest, python)<br/>no push, no GH token"]

    PL -- "spec.md, design.md" --> ORCH
    BL -- "edits on branch autose/issue-N" --> ORCH
    RV -- "review.md + verdict JSON<br/>(approve | changes: code | approach)" --> ORCH

    ORCH -- "stage 5" --> PR[(Pull request<br/>in the fork)]
    ORCH -- "status comment + artifacts" --> GH
    RV -. "review posted by orchestrator" .-> PR
    PR --> H2([Human decides merge or close])
```

**Who calls whom.** Only the orchestrator calls agents and GitHub. Agents never call each other; they communicate through files the orchestrator hands over (see ADR-003). The only component that holds the GitHub token is the orchestrator; agent subprocesses run with a stripped environment that contains the API key but no GitHub token (ADR-005).

**Back-edges (decided by the orchestrator, not by agents).**
- Stage 4 fail → stage 3 (budget 2 retries) → stage 2 once → stop with explanation.
- Stage 6 "changes: code" → stage 3; "changes: approach" → stage 2; at most 2 review rounds in total.
