# Requirements Specification: tinydb `count()` without a condition (Issue #3)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue reporter (unnamed) | To show "N records" on my page I do `db.count(...)` and I always have to invent a condition that is always true. |
| S2 | Issue reporter | Example: `db.count(where('id').exists())` is "not even right if docs don't have 'id'". |
| S3 | Issue reporter | `db.count()` with no arguments just raises a `TypeError`. |
| S4 | Issue reporter | It'd be nice if `count()` with nothing passed returned the total number of documents in the table. |
| S5 | Issue reporter | `count(some_query)` should keep working as today. |

Stakeholders available to answer: none. The reporter is the only source and is not reachable in this pipeline run.

Repository observation (not an external source): `tinydb/table.py` defines `Table.count(self, cond: QueryLike)` (line 709), which returns `len(self.search(cond))`. `Table.__len__` (line 725) returns `len(self._read_table())`, which is the total number of stored documents. S3 matches the current signature, where `cond` is required.

## 2. Purpose and scope

**In scope**
- Calling `Table.count()` with no argument returns the total number of documents in the table. Source: STATED (S4).
- Calling `count(cond)` with a query keeps its current result. Source: STATED (S5).

**Out of scope**
- Changing `search()`, `__len__()` or query semantics. Source: INFERRED (the issue asks only for `count()`; reasoning: the issue names no other API change).
- Counting in a different way, such as counting only documents that have a given field. Source: INFERRED (S2 describes a wrong workaround, not a request).
- Documentation and UI changes in the reporter's page. Source: INFERRED (S1 describes the reporter's own page).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| document | S4 | An entry stored in a tinydb table, as in the library API. | STATED term | — |
| table | S4 | A tinydb `Table` object. | STATED term | — |
| "nothing passed" | S4 | (a) no argument at all; (b) an explicit `count(None)`, which is also treated as no condition. | AMBIGUOUS | Q-01 |
| `db.count(...)` | S1 | (a) the reporter's shorthand for `table.count(...)` on the default table; (b) a `Database`-level method. This document does not verify which one exists. | AMBIGUOUS | Q-02 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user (application developer) | A developer who calls tinydb's `count()` in their own application to display a document total. | INFERRED (S1: the reporter calls `count()` on their page) |

## 5. Functional requirements

### FR-01: Count all documents when no condition is passed
Actor: ACT-01
Statement: WHEN `count()` is called with no condition argument, the system SHALL return the total number of documents currently stored in the table.
Source: STATED (S3, S4) | Readiness: NEEDS-CLARIFICATION (Q-01, Q-03)
Acceptance criteria:
- FR-01-AC1: a table holding 3 documents, `table.count()` is called with no arguments → the return value is `3`.
- FR-01-AC2: an empty table (no documents inserted), `table.count()` is called with no arguments → the return value is `0`.
- FR-01-AC3: a table where 2 of 5 documents were removed with `remove()`, `table.count()` is called with no arguments → the return value is `3`.
- FR-01-AC4: a table with 3 documents, `table.count()` is called with no arguments → no exception is raised (the current `TypeError` no longer occurs).
- FR-01-AC5: a table with 3 documents, `table.count(None)` is called → the return value is `3` (applies only if Q-01 is answered "treat as no condition").
Notes: The total is the same as `len(table)` for the same table. Repository check: `Table.__len__` returns `len(self._read_table())`. Readiness is held back because "nothing passed" is AMBIGUOUS (Q-01) and FR-01-AC5 depends on that answer. Related: ASM-01.

### FR-02: Keep count with a condition unchanged
Actor: ACT-01
Statement: WHEN `count(cond)` is called with a query condition, the system SHALL return the number of documents for which that query matches, as it does before this change.
Source: STATED (S5) | Readiness: NEEDS-CLARIFICATION (Q-03)
Acceptance criteria:
- FR-02-AC1: a table with documents `{"x": 1}`, `{"x": 2}`, `{"x": 1}`, `table.count(where('x') == 1)` is called → the return value is `2`.
- FR-02-AC2: a table with 3 documents, `table.count(where('x') == 99)` is called with no matches → the return value is `0`.
- FR-02-AC3: a table with 3 documents, `table.count()` with a condition argument whose query matches all documents → the return value equals `len(table)` (boundary case where the condition matches everything).
- FR-02-AC4: a table with 3 documents, `table.count(where('x').exists())` is called and one document lacks key `x` → the return value is `2` (documents without the field are not counted).
Notes: Readiness depends on the baseline being the current behaviour. Q-03 asks whether the existing test suite is the baseline. The baseline is INFERRED from S5 ("keep working as today"), not from a measured specification.

## 6. Non-functional requirements

None identified. The issue states no performance, reliability or security target. Performance of `count()` with no argument is not specified; see Q-04.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The change must not alter the result or the exception behaviour of `count(cond)` for existing valid calls. | STATED (S5) |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | The existing tinydb table storage (`_read_table()`), which provides the document list for the total. | INFERRED (repository read; `__len__` depends on it) | If the storage layer changes, the total may diverge from `len(table)`. See RSK-01. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | The no-argument total and `len(table)` could diverge if one of them is changed later. | Repository observation (`__len__`); S4 | Inconsistent counts across the API | Add a test that asserts `count() == len(table)` (FR-01-AC1 covers this). |
| RSK-02 | `count(None)` may be treated differently from `count()`, which changes the API contract. | Q-01 | Unexpected behaviour for callers who pass `None` | Answer Q-01 before implementation. |
| RSK-03 | The reporter's `db.count(...)` may refer to an API that does not exist in this library version. | Q-02 | The change may not reach the reporter's call site | Confirm Q-02 and the target object. |

## 10. External evidence log

No external evidence was needed. The issue names no law, standard, named product or external service, and makes no numeric claim about the outside world. No fetch call was made.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | — | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S3, S4) | Q-01, Q-03, ASM-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S5) | Q-03 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1) | — | — |
| CON-01 | — | STATED (S5) | — | — |
| DEP-01 | — | INFERRED (repository) | RSK-01 | — |
| Q-01 | — | — | blocks FR-01-AC5, RSK-02 | — |
| Q-02 | — | — | blocks RSK-03 | — |
| Q-03 | — | — | blocks FR-01, FR-02 | — |
| Q-04 | — | — | blocks NFR (none defined) | — |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | First draft from Issue #3. Two requirements, one constraint, one dependency, three risks, four open questions, one assumption. |

---

### Open questions

| Q | Question | Why it matters | Blocks | Priority | Ask whom | Status | Answer |
|---|---|---|---|---|---|---|---|
| Q-01 | Should `table.count(None)` return the total, the same as `count()` with no argument (a), or raise an error as a non-query (b)? | Determines FR-01-AC5 and the API contract. | FR-01-AC5, RSK-02 | P2 | Issue reporter or tinydb maintainers | OPEN | — |
| Q-02 | Is the reporter's `db.count(...)` meant as `Table.count` on the default table (a), or a new `Database.count` method (b)? | Determines where the change is made and whether RSK-03 applies. | RSK-03 | P3 | Issue reporter or tinydb maintainers | OPEN | — |
| Q-03 | Is the current behaviour of `count(cond)` (as in the repository today) the baseline for FR-02, including the test suite as the reference? | FR-02 relies on "as today" (S5), which has no measured reference. | FR-01, FR-02 | P2 | Tinydb maintainers | OPEN | — |
| Q-04 | Is there any performance target for the no-argument total on large tables? | Without it, no NFR can be measured. | NFR (none defined) | P3 | Issue reporter | OPEN | — |

No P1 questions are open. The readiness result below is driven by P2 questions and by the absence of READY requirements.

### Assumptions

| ASM | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-01 | `count()` with no argument counts every document currently stored in the table, including none removed (removed documents are not counted). | S4 ("total number of documents in the table") and the current `__len__` behaviour. | FR-01 | The expected total would differ from what the reporter needs. | Unconfirmed |

### Readiness and validation

- Requirements: 0 READY, 2 NEEDS-CLARIFICATION (FR-01, FR-02), 0 BLOCKED.
- Overall readiness: NOT READY, because no requirement is READY.
- Next actions: answer Q-01 and Q-03, then re-run validation (revision mode, version 0.2).