# Sequence view

> **Planned flow (written before any agent code).** After the first complete run this diagram is replaced by one drawn from the real run, with links to the Actions run, PR and review in `results/runs.md`.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant GH as GitHub (issue/PR/Actions)
    participant O as Orchestrator
    participant P as Planner (Haiku)
    participant B as Builder (Haiku)
    participant R as Reviewer (Sonnet)

    M->>GH: add label "autose" to issue #N
    GH->>O: start workflow (actor permission checked)
    O->>GH: status comment "run started"
    O->>P: issue (untrusted-wrapped) + skill
    P-->>O: spec.md
    O->>O: spec lint (testable ACs?)
    O->>P: spec.md + ARCHITECTURE.md + repo
    P-->>O: design.md
    O->>O: design lint (files/functions exist?)
    loop stage 3-4, max 2 retries, then 1 redesign
        O->>B: design.md + ACs, branch autose/issue-N
        B-->>O: code + tests (diff.patch)
        O->>O: compileall + pytest (own run)
        alt tests fail
            O->>B: failing output only
        end
    end
    O->>GH: push branch, open PR (stage 5)
    GH-->>O: CI result for PR head SHA
    loop review rounds, max 2
        O->>R: issue + diff + clean checkout at PR head SHA
        R->>R: read code, run pytest, try the issue's example
        R-->>O: review.md + verdict
        alt changes requested
            O->>B: reviewer findings (code) or P (approach)
        end
    end
    O->>GH: post review.md on PR, upload artifacts
    M->>GH: merge or close (human decision)
```
