# Requirements Specification: tinydb `count()` without a condition
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue author, unnamed): uses `db.count(...)` with an invented always-true condition to show a record count on a page.
- S2 (issue author, unnamed): `db.count()` with no arguments raises `TypeError`.
- S3 (issue author, unnamed): it would be useful if `count()` with nothing passed returned the total number of documents in the table.
- S4 (issue author, unnamed): `count(some_query)` keeps working as it does today.
- S5 (issue title, unnamed): "`count()` without a condition". Restates S2 and S3; no requirement of its own.

## 2. Purpose and scope
- In scope: `count()` with no condition returns the number of documents in the table (S2, S3). `count(query)` keeps its current result (S4).
- Out of scope: new query operators, changes to storages, changes to `update`/`remove`/`search` (no source requests them; INFERRED from S3 and S4 wording).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| no condition | S2, S3 | Options: (a) `count()` and `count(None)` both count all documents (see ASM-01); (b) `count(None)` keeps raising an error as today | AMBIGUOUS | Q-01 |
| total number of documents in the table | S3 | (a) all documents in the table, as `len(table)` (assumed, ASM-02); (b) only documents with an `id` field (rejected by S3 wording "total number") | ASSUMED (ASM-02) | — |
| `db.count()` | S2 | `TinyDB` forwards unknown attributes to the default table; no change to `database.py` needed | STATED | — |

Assumption register entries:
- ASM-01: `count(None)` behaves the same as `count()`. Basis: the no-argument call is the only case the issue names. Affects FR-01-AC4. If wrong, FR-01-AC4 is removed or changed to an error. Status: Unconfirmed.
- ASM-02: "total number of documents in the table" means every document stored in the table, with no field requirements. Basis: S3 and the issue's note that documents may lack an `id`. Affects FR-01, FR-03. If wrong, the count changes. Status: Unconfirmed.
- Q-01 (P2, blocks FR-01-AC4): should `count(None)` count all documents (ASM-01) or keep raising an error? Ask: the issue author. Status: OPEN.

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Code that calls `db.count()` or `table.count()` to show document totals (S1) | INFERRED (S1: the author calls the API from application code) |

## 5. Functional requirements

### FR-01: `count()` with no condition returns the table total
Actor: ACT-01
Statement: WHEN `count()` is called with no condition, the system SHALL return the number of documents stored in the table.
Source: STATED (S3) | Readiness: NEEDS-CLARIFICATION (Q-01, ASM-02)
Acceptance criteria:
- FR-01-AC1: a table holds 3 documents and `count()` is called with no arguments → returns 3 and raises no `TypeError`
- FR-01-AC2: a table is empty and `count()` is called with no arguments → returns 0
- FR-01-AC3: a table holds 2 documents with no `id` field and `count()` is called with no arguments → returns 2
- FR-01-AC4: a table holds 2 documents and `count(None)` is called → returns 2 (depends on Q-01 and ASM-01)
Notes: S2 is the failure being fixed. ASM-02 defines "total" as all documents.

### FR-02: `count(query)` keeps its current result
Actor: ACT-01
Statement: WHEN `count(query)` is called with a query, the system SHALL return the number of documents matching that query.
Source: STATED (S4) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: a table holds documents with `int` values 1, 1 and 2 and `count(where('int') == 1)` is called → returns 2
- FR-02-AC2: a table holds one document with `int` 1 and `count(where('int') == 99)` is called → returns 0 (no match boundary)
Notes: Existing behaviour, restated so the change is checked against it.

### FR-03: `count()` reflects the table's current contents
Actor: ACT-01
Statement: WHEN `count()` is called after a write, the system SHALL return the number of documents present at the time of the call.
Source: INFERRED (S3 "total number of documents in the table"; CON-02 forbids stale cache results) | Readiness: NEEDS-CLARIFICATION (ASM-02)
Acceptance criteria:
- FR-03-AC1: a table holds 1 document, one document is inserted, then `count()` is called → returns 2; that document is then removed and `count()` is called → returns 1
- FR-03-AC2: `count(query)` is called to fill the query cache, one document is inserted, then `count()` is called → returns the new total, not the cached value
Notes: Covers the cache risk in RSK-01.

## 6. Non-functional requirements
None identified.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | Standard library only; no new dependencies | STATED (ARCHITECTURE.md §1) |
| CON-02 | Table modifications go through `Table._update_table`, which clears the query cache; a total must not come from a stale cached result | STATED (ARCHITECTURE.md §3, rule 5) |

## 8. Dependencies
None identified.

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | The total could come from the query cache and be stale | CON-02, FR-03 | Wrong counts after writes | Compute the total from the table length, not the search cache (FR-03-AC2) |
| RSK-02 | `count(None)` behaviour is unclear | Q-01 | FR-01-AC4 may be wrong | Resolve Q-01; ASM-01 applies until then |

## 10. External evidence log
None identified. No external fact is involved, so no fetch call was made.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S3) | Q-01, ASM-01, ASM-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S4) | none | READY |
| FR-03 | ACT-01 | INFERRED (S3, CON-02) | ASM-02, RSK-01 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1) | FR-01, FR-02, FR-03 | — |
| CON-01 | — | STATED (ARCHITECTURE.md §1) | none | — |
| CON-02 | — | STATED (ARCHITECTURE.md §3) | RSK-01 | — |

## 12. Change log
| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial draft from issue #3 |