# Requirements Specification: tinydb `count()` without a condition
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue author): To show "N records" on my page I do `db.count(...)` and I always have to invent a condition that is always true.
- S2 (issue author): `db.count(where('id').exists())` is not even right if docs don't have 'id'.
- S3 (issue author): `db.count()` with no arguments just raises a `TypeError`.
- S4 (issue author): It'd be nice if `count()` with nothing passed returned the total number of documents in the table.
- S5 (issue author): `count(some_query)` should keep working as today.

## 2. Purpose and scope
- In scope: `count()` with no query returns the number of documents in the table (S4). `count(query)` keeps its existing result (S5).
- Out of scope: any change to `search`, `update`, `remove` or storage behaviour. No source for this exclusion beyond the issue focus (INFERRED from S4, S5).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "total number of documents" | S4 | Every document in the table, not only those with an `id` field (S2 implies this) | INFERRED | Q-01 |
| `count(None)` | Existing code path | Same as no argument, or an error | OPEN | Q-01 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Calls `db.count()` or `table.count()` from Python code to display totals | STATED (S1) |

## 5. Functional requirements

### FR-01: Count all documents when no query is given
Actor: ACT-01
Statement: WHEN `count()` is called with no argument, the system SHALL return the number of documents stored in the table.
Source: STATED (S4) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-01-AC1: a table holds three documents, one without an `id` field, and `db.count()` is called → returns 3
- FR-01-AC2: a table is empty and `db.count()` is called → returns 0
- FR-01-AC3: a table holds two documents, one is removed with `remove(where('name') == 'a')`, and `db.count()` is called → returns 1
- FR-01-AC4: a table holds two documents and `table.count(None)` is called → returns 2
Notes: AC4 depends on Q-01 (whether `None` is treated like no argument). Related: ASM-01.

### FR-02: Count matching documents when a query is given
Actor: ACT-01
Statement: WHEN `count(query)` is called with a query, the system SHALL return the number of documents matching the query.
Source: STATED (S5) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: three documents exist, two of which have `n == 2`, and `db.count(where('n') == 2)` is called → returns 2
- FR-02-AC2: one document exists and the query matches none of them → returns 0
- FR-02-AC3: one document lacks field `id` and one has it, and `db.count(where('id').exists())` is called → returns 1, while `db.count()` on the same table returns 2
Notes: The query result must not be replaced by the total (S2 motivation).

## 6. Non-functional requirements
None identified.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The change is limited to the `tinydb/` package and `tests/`; no new dependencies | STATED (task brief) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Python standard library only (no runtime dependencies) | EXTERNAL (ARCHITECTURE.md section 3) | None identified |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | `count(None)` may be treated differently from `count()` by maintainers | Q-01 | FR-01-AC4 may fail after review | Resolve Q-01 |

## 10. External evidence log
None identified. No external fact (law, standard, product capability) is used; no fetch call was needed.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | S4 | Q-01, ASM-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | S5 | None | READY |
| ACT-01 | n/a | S1 | None | n/a |

## 12. Change log
- 0.1 (2026-11-22): First draft from issue #3.

## Open questions and assumptions
- Q-01 (P2, blocks FR-01-AC4): Should `count(None)` return the total like `count()`, or raise an error? Options: (a) same as no argument, (b) error. Ask: issue maintainer.
- ASM-01: `count()` and `count(None)` are treated the same for the total. Basis: S4 and the `Table.count` docstring. Affects FR-01. Risk if wrong: FR-01-AC4 changes. Status: Unconfirmed.