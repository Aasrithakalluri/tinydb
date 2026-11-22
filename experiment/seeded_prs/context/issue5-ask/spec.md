---
# Requirements Specification: tinydb result ordering (Issue #5)
Version: 0.2 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY (FR-03 and FR-04 are READY; FR-01 and FR-02 wait on open P2 questions Q-04 and Q-05; no P1 question is open)

## 1. Input record
Speaker for all sentences: issue reporter (a library user, unnamed), except S6 and S7, which are the maintainer's answers. Source: GitHub issue #5 of Aasrithakalluri/tinydb.
- S1: "Results come back in a strange order" (issue title).
- S2: "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right."
- S3: "I don't know exactly when it happens, but it seems related to how I created or changed the documents."
- S4: "It also looks different after I close and reopen the program."
- S5: "I'd like the order to be sensible and predictable, so my page doesn't jump around."
- S6 (maintainer): "1a, 2a, 3a." Answers to Q-01, Q-02 and Q-03: ascending doc_id; an updated document keeps its position; built-in JSON and in-memory storage only.
- S7 (maintainer): "Ascending doc_id is stable across reopens, insertion order is not once the JSON file is rewritten with sorted keys." This is the maintainer's reasoning about storage internals. It is recorded, not verified against the code, and no requirement depends on it alone.

Repository check (read-only, from the previous revision): `Table.all()` (tinydb/table.py:235-247) and `Table.search()` (tinydb/table.py:249-297) build results by iterating the stored table dict (`_read_table()`, lines 272-276 and 740-742). Neither method sorts. The reported misordering was not reproduced (RSK-01).

## 2. Purpose and scope
**In scope:**
- The order of documents returned by `Table.all()` and `Table.search()` (S2, S5). Order is ascending doc_id (S6, Q-01).
- Order after an update keeps each document's position (S3; S6, Q-02).
- Order after closing and reopening a database that uses built-in JSON storage (S4; S6, Q-03).
- Built-in JSON and in-memory storage only (S6, Q-03).

**Out of scope:**
- Custom `Storage` subclasses. Their order is not guaranteed by this specification (S6, Q-03).
- Adding a new sort parameter or sort API (ASM-04; no statement asks for one).
- Ordering of `get(doc_ids=...)` results (ASM-04).
- Changes to storage file formats beyond what ordering requires (ASM-04).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "sensible" / "predictable" order (S5) | S5; S6 | Ascending doc_id, as answered by the maintainer | RESOLVED (CONFIRMED) | Q-01 |
| "changed" documents (S3) | S3; S6 | Updated in place, position kept | RESOLVED (CONFIRMED) | Q-02 |
| "doesn't jump around" (S5) | S5 | Results keep their relative order across repeated calls and across updates of other documents | Interpreted through FR-02 and FR-03 | Q-01, Q-02 |
| "reopen" (S4) | S4; S6 | Closing and reopening a database that uses built-in JSON storage | RESOLVED for built-in storage; custom storage out of scope | Q-03 |
| "strange" / "doesn't look right" (S1, S2) | S1, S2 | No measurable definition of wrong order; a reproduction is needed | AMBIGUOUS | Q-05 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user (application developer) | Calls `db.all()` and `db.search(...)` in Python code and renders the results (S2, S5) | INFERRED (from S2: the reporter calls these methods; needs confirmation) |

## 5. Functional requirements

### FR-01: all() returns documents in ascending doc_id order
Actor: ACT-01
Statement: WHEN `all()` is called on a table, the system SHALL return the table's documents in ascending `doc_id` order.
Source: CONFIRMED (Q-01, maintainer, S6; basis S1, S2, S5) | Readiness: NEEDS-CLARIFICATION (Q-04, P2)
Acceptance criteria:
- FR-01-AC1: a table where documents are inserted with auto IDs 1, 2, 3 → `all()` returns doc_ids [1, 2, 3] in that order.
- FR-01-AC2: documents inserted with explicit doc_id values 3, then 1, then an auto-ID insert (id 4) → `all()` returns doc_ids [1, 3, 4].
- FR-01-AC3: `insert_multiple` of documents with explicit doc_ids [5, 2] into an empty table → `all()` returns doc_ids [2, 5].
- FR-01-AC4: an empty table → `all()` returns an empty list [].
Notes: The ordering rule is confirmed. Readiness stays NEEDS-CLARIFICATION only because Q-04 (cost of sorting on each call, P2) is still linked to this requirement. Current behaviour is not reproduced (RSK-01). Changed behaviour for users who relied on insertion order is recorded in RSK-04.

### FR-02: search() returns matches in the same relative order as all()
Actor: ACT-01
Statement: WHEN `search(cond)` is called on a table, the system SHALL return the matching documents in the same relative order that `all()` uses.
Source: ASSUMED (ASM-02; basis S2; consistent with Q-01 answer, which does not state search order explicitly) | Readiness: NEEDS-CLARIFICATION (Q-05, P2; ASM-02 unconfirmed)
Acceptance criteria:
- FR-02-AC1: documents with doc_ids 1 to 4 exist, and `cond` matches doc_ids 4 and 2 → `search(cond)` returns doc_ids [2, 4].
- FR-02-AC2: `cond` matches no document → `search(cond)` returns an empty list [].
- FR-02-AC3: `search(cond)` is run once, then a new document matching `cond` is inserted with a doc_id lower than the existing matches, then `search(cond)` is run again → the second result includes the new document in ascending doc_id position (no stale cached order).
Notes: The query cache in `Table.search` (table.py:265-295) must not return an out-of-order list after a write. FR-02-AC3 tests that. The maintainer should confirm ASM-02 explicitly, because Q-01 answered only for `all()`.

### FR-03: update keeps a document's position in results
Actor: ACT-01
Statement: WHEN a document is updated with `update()` or `upsert()`, the system SHALL keep that document at the same position in `all()` and `search()` results.
Source: CONFIRMED (Q-02, maintainer, S6; basis S3) | Readiness: READY
Acceptance criteria:
- FR-03-AC1: documents with doc_ids 1, 2, 3 exist, and `update({'x': 9}, doc_ids=[2])` is run → `all()` returns doc_ids [1, 2, 3].
- FR-03-AC2: `update` with a condition that matches no document → `all()` returns the same doc_id order as before the call.
- FR-03-AC3: `upsert` of a document with a new explicit doc_id 0 → `all()` returns doc_ids [0, 1, 2, 3].
Notes: The criteria are checked through the order rule in FR-01. FR-03-AC3 covers the boundary case where the new document lands first in the order. Because the position is set by doc_id, this holds without a separate position store.

### FR-04: order is unchanged after close and reopen
Actor: ACT-01
Statement: WHEN a database that uses the built-in JSON storage is closed and reopened, the system SHALL return `all()` documents in ascending `doc_id` order.
Source: CONFIRMED (S4 reports the reopen difference; Q-01 and Q-03, maintainer, S6) | Readiness: READY
Acceptance criteria:
- FR-04-AC1: a JSON database where documents are inserted with explicit doc_ids 3, 1, 2 is closed and reopened → `all()` returns doc_ids [1, 2, 3].
- FR-04-AC2: a document with doc_id 2 is removed from a three-document JSON database, which is then closed and reopened → `all()` returns doc_ids [1, 3].
- FR-04-AC3: an empty JSON database file is reopened → `all()` returns an empty list [].
Notes: Sorting on read (FR-01) makes the result independent of the order stored in the file. That means the reopen behaviour does not depend on the file format. Custom `Storage` classes are out of scope (S6, Q-03).

## 6. Non-functional requirements
None identified. No metric or threshold was stated. A cost limit for sorting on each call is unknown: TBD (Q-04). See RSK-02.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| None identified | No constraint on time, budget, platform or technology is stated in the input. | None |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Built-in storage classes (JSON file and in-memory) that the library provides | INFERRED (S4 implies a file-backed database; scope confirmed by S6) | If the built-in JSON storage changes, FR-04 must be re-verified (RSK-03). |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | The misordering is not reproduced. The cause may be elsewhere (for example in caching), so a sort alone may not fix it. | S2, S3, Q-05 | Fix may not address the reported bug. | Ask for a minimal reproduction (Q-05) before implementation. |
| RSK-02 | Sorting on each `all()` or `search()` call adds cost for large tables. | FR-01, Q-04 | Slower reads for big tables; no threshold to test against. | Answer Q-04; add a measurable NFR. |
| RSK-03 | Changes to the built-in JSON storage could break the reopen order. | S4, DEP-01 | FR-04 would fail without a test. | Keep FR-04 tests in the suite. |
| RSK-04 | Users who relied on insertion order in `all()` or `search()` will see a different order after the change. | Q-01 answer (S6) | Behaviour change for existing code. | Maintainer to decide whether to note this in release notes (not yet asked). |

## 10. External evidence log
None. No external fact (law, standard, product capability) is needed. No fetch call was made. The behaviour was checked from repository code only, and the maintainer's storage reasoning (S7) was not verified.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | CONFIRMED (Q-01, S6) | Q-04 (P2); RSK-01, RSK-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | ASM-02 (S2) | Q-05 (P2); RSK-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | CONFIRMED (Q-02, S6) | none open | READY |
| FR-04 | ACT-01 | CONFIRMED (S4; Q-01, Q-03, S6) | RSK-03 | READY |
| ACT-01 | n/a | INFERRED (S2) | n/a | n/a |
| DEP-01 | n/a | INFERRED (S4) | RSK-03 | n/a |
| ASM-01 | n/a | CONFIRMED (Q-01, S6) | n/a | Confirmed |
| ASM-02 | n/a | ASSUMED | Q-05 | Unconfirmed |
| ASM-03 | n/a | CONFIRMED (Q-02, S6) | n/a | Confirmed |
| ASM-04 | n/a | ASSUMED | none | Unconfirmed |
| RSK-01 to RSK-04 | n/a | n/a | Q-05, Q-04, Q-03, Q-01 | Open |

Open questions:
- Q-04 (P2): acceptable cost of sorting on each `all()` or `search()` call. Blocks FR-01 and the NFR. Ask: what is the largest table size and maximum added latency the maintainer accepts?
- Q-05 (P2): minimal reproduction of the reported order. Blocks FR-02 and confirms RSK-01. Ask: can the reporter provide a short script showing the wrong order, with the steps that produce it?

Resolved in revision 0.2:
- Q-01 (ascending doc_id), answered by the maintainer (S6).
- Q-02 (an update keeps position), answered by the maintainer (S6).
- Q-03 (built-in storage only), answered by the maintainer (S6).

## 12. Change log
- 0.1 (2026-11-22): first draft from issue #5. Interpretation ASM-01 (ascending doc_id) chosen because the input does not define "sensible" or "predictable". Repository read to confirm current code paths (no sort in `all()` or `search()`).
- 0.2 (2026-11-22): maintainer answers applied. Q-01 → ascending doc_id (ASM-01 CONFIRMED). Q-02 → updates keep position (ASM-03 CONFIRMED). Q-03 → built-in JSON and in-memory storage only (custom storage moved to out of scope). FR-03 and FR-04 are READY. FR-01 and FR-02 stay NEEDS-CLARIFICATION because of open P2 questions Q-04 and Q-05. Added RSK-04 for the behaviour change. Answered questions Q-01 to Q-03 dropped from the open list. Overall readiness moved from NOT READY to PARTIALLY READY.

Assumptions register (ASM):
- ASM-01: result order for `all()` is ascending doc_id. CONFIRMED (Q-01, maintainer, S6).
- ASM-02: `search()` uses the same relative order as `all()`. Unconfirmed; the maintainer's answer covers `all()` only.
- ASM-03: an update does not move a document in the order. CONFIRMED (Q-02, maintainer, S6).
- ASM-04: no new sort API, no change to `get(doc_ids=...)` order, and no storage file format change beyond what ordering requires are in scope. Unconfirmed.