# Requirements Specification: tinydb `count()` without a condition (Issue #3)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| S# | Speaker | Text (issue #3) |
|---|---|---|
| S1 | Issue author (reporter) | To show "N records" on my page I do `db.count(...)` and I always have to invent a condition that is always true: |
| S2 | Issue author (reporter) | `db.count(where('id').exists())   # not even right if docs don't have 'id'` |
| S3 | Issue author (reporter) | `db.count()` with no arguments just raises a `TypeError`. |
| S4 | Issue author (reporter) | It'd be nice if `count()` with nothing passed returned the total number of documents in the table. |
| S5 | Issue author (reporter) | `count(some_query)` should keep working as today. |

Stakeholders available to answer questions: none. The reporter is the only known stakeholder and cannot be reached in this pipeline run, so all open questions stay open.

Repository check (read-only, no external evidence): `Table.count(self, cond)` is defined at `tinydb/table.py:709` and returns `len(self.search(cond))`. It has no default for `cond`, which explains the `TypeError` in S3. `Table.__len__` (`tinydb/table.py:725`) already returns the total document count. `Database` has no `count` method. `Database.__len__` (`tinydb/database.py:260`) counts only the default table.

## 2. Purpose and scope

**In scope**
- Calling `count()` with no argument returns the total number of documents in the table. Source: STATED (S4).
- Calling `count(cond)` with a query keeps its current result. Source: STATED (S5).

**Out of scope**
- Changes to `search()`, `all()`, `__len__` or any other query behaviour. Source: INFERRED (not mentioned in input; the issue concerns only `count()`).
- Adding a `count` method to `Database`. Source: OPEN (Q-02).

**Assumptions**
- ASM-01: "`db`" in the issue refers to a `Table` object, so the change applies to `Table.count`. Source: ASSUMED. Basis: `Table.count` is the only `count` method in the repository and `Database` has none. If wrong, FR-01 changes. Linked: Q-02.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "db" (S1, S2) | S1, S2 | (a) a `Table` object (matches the repository); (b) a `Database` object, which would need a new method | AMBIGUOUS | Q-02 |
| "nothing passed" / "no arguments" (S4) | S4 | (a) no argument at all; (b) an explicit `None` argument also passed | AMBIGUOUS | Q-01 |
| "the table" (S4) | S4 | The table on which `count()` is called | Clear | — |
| "total number of documents" (S4) | S4 | Every document stored in that table, including documents without an `id` field (S2 implies this is the intent) | Clear | — |
| "as today" (S5) | S5 | Same results as the current `count(cond)` implementation for valid queries | Clear | — |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer using tinydb | Calls `count()` on a table in their code to display document totals or filtered totals. | INFERRED (S1: the reporter calls `count` in application code to show a number on a page) |

## 5. Functional requirements

### FR-01: Count all documents when no argument is given
Actor: ACT-01
Statement: WHEN `count()` is called with no argument, the system SHALL return the total number of documents in the table.
Source: STATED (S4) | Readiness: NEEDS-CLARIFICATION (Q-02, ASM-01)
Acceptance criteria:
- FR-01-AC1: a table contains 3 documents and `count()` is called with no argument → the call returns 3.
- FR-01-AC2: a table contains no documents and `count()` is called with no argument → the call returns 0.
- FR-01-AC3: a table contains 2 documents without an `id` field and 1 document with an `id` field, and `count()` is called with no argument → the call returns 3.
- FR-01-AC4: a table contains 3 documents, one document is removed, and `count()` is called with no argument → the call returns 2.
Notes: The reporter's concern in S2 is that a filter on `id` misses documents without that field. FR-01-AC3 checks that the no-argument form does not filter. Q-02 decides whether this change applies to `Table` only or also to `Database`. Related: RSK-02.

### FR-02: Keep counting documents that match a query
Actor: ACT-01
Statement: WHEN `count(cond)` is called with a query, the system SHALL return the number of documents in the table that match the query.
Source: STATED (S5) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: a table contains 3 documents, 2 of which have field `x` equal to 1, and `count(where('x') == 1)` is called → the call returns 2.
- FR-02-AC2: a table contains 3 documents, none of which match the query, and `count(where('x') == 99)` is called → the call returns 0.
- FR-02-AC3: a table contains 2 documents with an `id` field and 2 without, and `count(where('id').exists())` is called → the call returns 2, not the total of 4.
- FR-02-AC4: a table contains no documents and `count(where('x') == 1)` is called → the call returns 0.
Notes: The baseline is the current `len(self.search(cond))` at `tinydb/table.py:716`. FR-02 is a regression requirement, so the new no-argument path must not change this result.

### FR-03: Behaviour when `None` is passed explicitly
Actor: ACT-01
Statement: IF `count(None)` is called with an explicit `None` argument, THEN the system SHALL return the total number of documents in the table.
Source: ASSUMED (ASM-02: an explicit `None` is treated the same as no argument; the input does not say this) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-03-AC1: a table contains 3 documents and `count(None)` is called → the call returns 3.
- FR-03-AC2: a table contains no documents and `count(None)` is called → the call returns 0.
Notes: The alternative is to keep today's behaviour for `None`, which is an error from the query path (not verified; no test run). If Q-01 chooses that option, FR-03 becomes SUPERSEDED or is rewritten as a failure requirement. Related: RSK-01.

## 6. Non-functional requirements

None identified. The input states no performance, reliability or security target.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| — | None identified. The input sets no time, budget, platform or technology limit. | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| — | None identified. The change depends only on the existing tinydb table code. | — | — |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Making `cond` optional may change how an explicit `None` argument behaves for existing callers. | Q-01, FR-03 | Callers that rely on the current error for `count(None)` would silently get a number. | Get the answer to Q-01 before changing the signature. |
| RSK-02 | The issue may refer to `Database`, which has no `count` method. | S1, S2, ASM-01, Q-02 | The change could be made on the wrong API, and the reporter's code would still fail. | Get the answer to Q-02 before implementation. |

Escalation (human decision needed): the reporter or the tinydb maintainer must answer Q-01 and Q-02. No stakeholder was available in this run.

## 10. External evidence log

None. The issue mentions no law, standard, product or external service, and the questions depend only on the repository code. No fetch calls were made.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| — | None | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S4) | Q-02, ASM-01, RSK-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S5) | none open | READY |
| FR-03 | ACT-01 | ASSUMED (ASM-02) | Q-01, RSK-01 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1) | — | — |
| ASM-01 | — | ASSUMED | Q-02 | — |
| ASM-02 | — | ASSUMED | Q-01 | — |
| Q-01 | — | — | blocks FR-03, RSK-01 | — |
| Q-02 | — | — | blocks FR-01, RSK-02 | — |
| RSK-01 | — | S4, FR-03 | Q-01 | — |
| RSK-02 | — | S1, S2, ASM-01 | Q-02 | — |

Open questions:
- Q-01 (P2): When `count` is called with an explicit `None`, should it (a) return the total number of documents, or (b) raise an error as it does today? Blocks FR-03 and RSK-01. Ask: reporter or maintainer.
- Q-02 (P2): Does "`db`" mean a `Table` object (change `Table.count` only), or should `Database` also get a `count()` that counts its default table? Blocks FR-01 and RSK-02. Ask: reporter or maintainer.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from issue #3. FR-01 and FR-03 need clarification; FR-02 is ready. Overall readiness: PARTIALLY READY. |