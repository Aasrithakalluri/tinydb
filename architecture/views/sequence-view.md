# Sequence view: one real run (issue #3, `count()` without a condition)

This is drawn from the real run logs, not from the plan. The earlier planned diagram is in the git history (PR #7).

- Issue: [#3](https://github.com/Aasrithakalluri/tinydb/issues/3) · PR: [#10](https://github.com/Aasrithakalluri/tinydb/pull/10)
- Run that finished the work: [44995345522](https://github.com/Aasrithakalluri/tinydb/actions/runs/44995345522). Stages 1-4 were done by run [44994878885](https://github.com/Aasrithakalluri/tinydb/actions/runs/44994878885); the later runs resumed from its artifact (see ADR-011). Times are UTC on 2026-11-22.
- Costs and turn counts are from `state.json` (`calls`). Total: $0.058, 298k input and 19k output tokens.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant GH as GitHub
    participant O as Orchestrator
    participant P as Planner (Haiku)
    participant B as Builder (Haiku)
    participant R as Reviewer (Sonnet)

    M->>GH: label "autose" on issue #3
    GH->>O: issues:labeled, write permission checked
    O->>GH: status comment "started"
    Note over O,P: 06:42:51 stage 1, 4 turns, $0.007
    O->>P: issue (untrusted tags) + A1 skill
    P-->>O: spec.md (10 acceptance criteria)
    O->>O: spec lint: pass
    Note over O,P: 06:43:05 stage 2, 6 turns, $0.004
    O->>P: spec.md + ARCHITECTURE.md
    P-->>O: design.md
    O->>O: design lint FAILS: test symbol not found
    O->>P: failing check text
    P-->>O: design.md (fixed, $0.003)
    O->>O: design lint: pass
    Note over O,B: 06:43:13 stage 3, 9 turns, $0.003, 2 tool calls denied
    O->>B: MODE IMPLEMENT + design.md + criteria
    B-->>O: edits to tinydb/table.py
    O->>O: compileall + import + scope check: pass (diff 24 lines)
    Note over O,B: 06:43:26 stage 4, 10 turns, $0.003, 1 tool call denied
    O->>B: MODE TEST + criteria
    B-->>O: tests in tests/test_tables.py
    O->>O: runs full pytest itself: pass, every AC has a test
    Note over O,GH: run died at stage 5 (PR creation not allowed); restarted twice (ADR-011)
    O->>O: restart: re-apply diff.patch on base commit
    O->>GH: push autose/issue-3, reuse PR #10
    O->>GH: dispatch CI, wait for workflow_dispatch run
    GH-->>O: CI success (06:50:33)
    Note over O,R: 06:50:51 stage 6, 5 turns, $0.038, 2 tool calls denied
    O->>R: issue + diff + clean checkout at PR head
    R->>R: Read code, run pytest (248 pass), python -c experiments
    R-->>O: review + JSON verdict approve, tests run = true
    O->>GH: post review on PR #10, status DONE
    M->>GH: decides whether to merge (not done by the workflow)
```

## What the real run shows that the plan did not
- **Design lint paid for itself:** the Planner named a test symbol that did not exist; the check caught it and one retry fixed it, before any code was written.
- **Restart path:** stage 5 failed twice for pipeline reasons (a repo setting, then restore and duplicate-PR bugs). The restart logic (ADR-011) is part of the real flow.
- **Denied tool calls:** the Builder and the Reviewer each tried tool calls that the policy denied (5 in total across the run). The log keeps only the count; the orchestrator now also records what was denied (ADR-005 evidence).
- **Cost split:** the Reviewer (Sonnet) was 66% of the cost while writing 7% of the output tokens; the three Haiku stages together cost $0.020.
