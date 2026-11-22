# Requirements Specification: Predictable document order for all() and search()
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record
- S1 (issue author): "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right."
- S2 (issue author): "I don't know exactly when it happens, but it seems related to how I created or changed the documents."
- S3 (issue author): "It also looks different after I close and reopen the program."
- S4 (issue author): "I'd like the order to be sensible and predictable, so my page doesn't jump around."
- Stakeholders available to answer: none (single issue author, unavailable).

## 2. Purpose and scope
- In scope: the order in which `Table.all()` and `Table.search()` return documents, including after updates, cached repeats, and a reopen of a JSON database. Source: S1, S2, S3, S4.
- Out of scope: sorting by any field other than the document id; changes to the storage interface. Source: ASM-02 (not stated in input).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "sensible" | S4 | (a) ascending document id; (b) insertion order; (c) sorted by a field value | AMBIGUOUS | Q-01 |
| "predictable" | S4 | Same input state always yields the same order (assumed) | AMBIGUOUS | Q-01 |
| "doesn't look right" | S1 | Not measurable; taken as "not ascending by document id" | AMBIGUOUS | Q-01 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Calls `db.all()` / `db.search()` and renders results in order | INFERRED (S1, S4: "my page") |

## 5. Functional requirements

### FR-01: all() returns documents in ascending document id order
Actor: ACT-01
Statement: WHEN the caller invokes `Table.all()`, the system SHALL return every document of the table sorted by ascending integer document id.
Source: ASSUMED (ASM-01) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-01-AC1: documents inserted with explicit ids 3, 1, 2 in that order → `all()` returns ids [1, 2, 3]
- FR-01-AC2: table emptied by truncate (boundary: no documents) → `all()` returns []
Notes: ASM-01 chooses option (a) from the glossary. S2 and S3 are the reason the order must not depend on write history or storage key order.

### FR-02: search() returns matches in ascending document id order
Actor: ACT-01
Statement: WHEN the caller invokes `Table.search(cond)`, the system SHALL return every matching document sorted by ascending integer document id.
Source: ASSUMED (ASM-01) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: documents with ids 10 and 2 matching a condition, inserted in that order → `search(cond)` returns ids [2, 10] (numeric, not text, order)
- FR-02-AC2: the same search run twice with no write in between (cache hit on second run) → second result has the same ids in the same order as the first, [4, 7]
- FR-02-AC3: search condition that matches no document (boundary) → `search(cond)` returns []
Notes: AC2 covers the query cache path, which returns cached results.

### FR-03: document order is unchanged by updates and by reopening a database
Actor: ACT-01
Statement: WHEN a document is updated or a JSON database is closed and reopened, the system SHALL keep `all()` in ascending document id order.
Source: ASSUMED (ASM-01) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-03-AC1: document with id 1 updated in a table holding ids 1, 2, 3 → `all()` returns ids [1, 2, 3] and the updated value is readable by `get(doc_id=1)`
- FR-03-AC2: JSON database with ids 3, 1, 2 inserted, closed, then reopened → `all()` returns ids [1, 2, 3]
- FR-03-AC3: JSON database opened with `sort_keys=True` holding ids 1, 2, 10, closed, then reopened (boundary: ids 10 and 2 would sort differently as text) → `all()` returns ids [1, 2, 10]
Notes: S3 "looks different after reopen" is the reason for AC2 and AC3.

## 6. Non-functional requirements
None identified (the issue states no measurable quality).

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | No new runtime dependencies; standard library only | STATED (ARCHITECTURE.md §1) |
| CON-02 | Storage interface (`read()` / `write()`) and the `_update_table` write path are unchanged | STATED (ARCHITECTURE.md §3, constraints 1, 2, 5) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Storage returns the full table dict on `read()` | STATED (ARCHITECTURE.md §3, constraint 2) | Order cannot be restored from storage without this |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Author meant insertion order, not id order | Q-01 | Wrong order is enforced; FR-01 to FR-03 must be rewritten | Confirm option (a) or (b) with the author |
| RSK-02 | Sorting on every uncached search adds cost on large tables | Assumption (no performance figure given) | Slower uncached searches | Measure only if the author states a size; TBD (Q-02) |

## 10. External evidence log
| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | No external fact is used by this specification | n/a | n/a | n/a | n/a | n/a | None |

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | ASM-01 (S1, S4) | Q-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | ASM-01 (S1, S4) | Q-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASM-01 (S2, S3) | Q-01 | NEEDS-CLARIFICATION |
| CON-01 | n/a | STATED | none | READY |
| CON-02 | n/a | STATED | none | READY |

## 12. Change log
- 0.1 (2026-11-22): first draft from issue #5. Interpretation ASM-01 (ascending document id) applied to all open ambiguity.

Open questions:
- Q-01 (P1): Which order should results follow: (a) ascending document id, (b) insertion order, or (c) a field value? Blocks FR-01, FR-02, FR-03.
- Q-02 (P3): Is there a table size at which uncached search speed matters? Blocks nothing; affects RSK-02.