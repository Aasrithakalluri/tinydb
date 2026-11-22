# Requirements Specification: tinydb result ordering (issue #5)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record
- S1 (issue author, unnamed): "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right."
- S2 (issue author): "I don't know exactly when it happens, but it seems related to how I created or changed the documents."
- S3 (issue author): "It also looks different after I close and reopen the program."
- S4 (issue author): "I'd like the order to be sensible and predictable, so my page doesn't jump around."

Stakeholders available to answer: none (the issue author is not reachable in this session).

## 2. Purpose and scope
- In scope: the order in which `Table.all()`, `Table.search(cond)` and default-table `db.all()` / `db.search()` return documents (S1, S4).
- In scope: order stability across document changes (S2) and across close and reopen of a JSON database (S3).
- Out of scope: sort keys chosen by the caller, and the order returned by `get()` (first match), are not covered by this specification. The issue does not mention them (INFERRED: no requirement; see Q-03, Q-04).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| sensible | S4 | (a) ascending document ID; (b) insertion order; (c) last-modified order | AMBIGUOUS | Q-01 |
| predictable | S4 | Same order on every call and after reopen, whichever option is chosen | AMBIGUOUS | Q-01 |
| changed (documents) | S2 | Update in place, or remove and re-insert | AMBIGUOUS | Q-01 |
| document ID | ARCHITECTURE.md §1 | Integer id of a document (repository document) | STATED | — |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | A developer using tinydb in a program who calls `all()` and `search()` (S1) | INFERRED (S1: the issue author reads results from these calls; needs confirmation) |

## 5. Functional requirements

### FR-01: Results are returned in ascending document ID order
Actor: ACT-01
Statement: WHEN `all()` or `search(cond)` is called, the system SHALL return the matching documents in ascending document ID order.
Source: ASSUMED (ASM-01), basis S4   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-01-AC1: documents inserted with explicit IDs 3, 1, 2 in that order → `all()` returns IDs [1, 2, 3]
- FR-01-AC2: empty table → `all()` and `search(lambda doc: True)` return an empty list
- FR-01-AC3: table with IDs 5, 2, 4 where only IDs 4 and 5 match a condition → `search(cond)` returns IDs [4, 5], and a condition matching only ID 2 returns [2]
Notes: ASM-01. Related Q-01 (P1). Blocks the choice between options (a), (b) and (c).

### FR-02: Changing a document does not alter the order of the others
Actor: ACT-01
Statement: WHEN a document is updated in place, the system SHALL keep its document ID and its position in the ascending ID order.
Source: INFERRED (S2 names changes as the cause; the expected result follows FR-01), needs confirmation   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: table with IDs 1, 2, 3 where document 1 is updated → `all()` returns IDs [1, 2, 3] with document 1 holding the new value
- FR-02-AC2: document 2 is removed from IDs 1, 2, 3 and a new document without an explicit ID is inserted → the new document gets ID 4 and `all()` returns IDs [1, 3, 4]
Notes: ASM-01, Q-01.

### FR-03: The order is the same after closing and reopening a JSON database
Actor: ACT-01
Statement: WHEN a JSON database is closed and reopened, the system SHALL return the same ascending document ID order from `all()`.
Source: STATED (S3) with ASM-01   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-03-AC1: JSON database with documents inserted as IDs 10, 2, 1 → after close and reopen, `all()` returns IDs [1, 2, 10] (numeric, not string, order)
- FR-03-AC2: JSON database with no documents → after close and reopen, `all()` returns an empty list
Notes: S3 states the reopen effect; ASM-01 fixes the expected order.

## 6. Non-functional requirements
None identified. (The issue states no measurable quality. Sorting cost is recorded as RSK-02.)

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | No new runtime dependencies; standard library only (ARCHITECTURE.md §1) | STATED (repository document, not an S#) |
| CON-02 | Layering: `table.py` must not gain imports of other package modules; storages are only used through `Storage` (ARCHITECTURE.md §3, rule 4) | STATED (repository document) |
| CON-03 | Every table modification goes through `Table._update_table`, which clears the query cache (ARCHITECTURE.md §3, rule 5) | STATED (repository document) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | None identified | — | — |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Callers who rely on the old insertion order see different results | Q-01, Q-02 | Breaking change for existing programs | Confirm the chosen order with the author before release; note it in the changelog |
| RSK-02 | Sorting on every `all()`, `search()` and iteration costs O(n log n) per call | ASM-01 (design choice) | Slower reads on large tables | Measure on large tables if this matters; no threshold is known (TBD) |
| RSK-03 | `get(cond)` returns the first match in storage order and may disagree with `search` | Q-04 | Inconsistent results between methods | Ask Q-04 |

## 10. External evidence log
None. No external fact (law, standard, product capability) is involved. No fetch call was made.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | ASSUMED (ASM-01), S4 | Q-01, ASM-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | INFERRED (S2) | Q-01, ASM-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | STATED (S3) | Q-01, ASM-01 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1) | Q-01 | NEEDS-CLARIFICATION |
| CON-01 to CON-03 | — | STATED (repository) | — | READY |

## 12. Change log
- 0.1 (2026-11-22): first draft from issue #5. Requirements are ASSUMED or INFERRED and stay open until Q-01 is answered.