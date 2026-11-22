# Requirements Specification: tinydb search result isolation (Issue #2)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record
- S1 (reporter, issue #2): "Modifying a document I got from `search()` changes what later searches return."
- S2 (reporter): "I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file."
- S3 (reporter): "If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong."
- S4 (reporter): "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result."

## 2. Purpose and scope
- In scope: documents returned by `Table.search()` (and `TinyDB.search()`) must not change what later identical searches return. Source: STATED (S2, S4).
- Out of scope: changes to on-disk file format; changes to `update()` or other write paths. Source: INFERRED (S3, the file is correct).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "stored data" | STATED (S4) | Options: (a) the data in the storage backend; (b) the data as of the last write. Both are assumed equal here. | ASSUMED (ASM-01) | Q-01 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Python code that calls `search()` and mutates the returned dicts (S2). | STATED (S2) |

## 5. Functional requirements

### FR-01: Top-level changes to a result do not reach later searches
Actor: ACT-01
Statement: WHEN a caller changes a top-level key of a document returned by `search()`, the system SHALL return the stored value for that key on every later identical search.
Source: STATED (S2, S4)   |   Readiness: BLOCKED (CNF-01)
Acceptance criteria:
- FR-01-AC1: a document with name 'a' is returned by search, then its 'name' is set to 'CHANGED' → a second identical search returns name 'a'.
- FR-01-AC2: a document is returned by search, then a new key 'extra' is added to it → a second identical search returns the document without key 'extra'.
- FR-01-AC3: a document is returned by search, then its 'name' is set to 'CHANGED' and the database is closed → the JSON file still contains name 'a'.
Notes: AC1 and AC2 fail on the current code; AC3 passes today. CNF-01 with the existing test `test_query_cache_documents_are_shared_with_cache` (tests/test_tinydb.py:732).

### FR-02: Nested changes to a result do not reach later searches or storage
Actor: ACT-01
Statement: WHEN a caller changes a nested value of a document returned by `search()`, the system SHALL keep the stored nested value unchanged for every later search and for `all()`.
Source: STATED (S2, S4)   |   Readiness: BLOCKED (CNF-01)
Acceptance criteria:
- FR-02-AC1: a document with tags ['x'] is returned by search, then 'oops' is appended to its 'tags' → a second identical search returns tags ['x'].
- FR-02-AC2: a document with tags ['x'] is returned by search, then 'oops' is appended to its 'tags' on an in-memory database → `all()` returns tags ['x'].
- FR-02-AC3: an identical search is served from the cache, then 'oops' is appended to a nested 'tags' list of its result → a third identical search returns tags ['x'].
Notes: all three fail on the current code. Conflicts with the existing test in CNF-01.

### FR-03: The returned list is independent of later searches
Actor: ACT-01
Statement: WHEN a caller changes the list returned by `search()`, the system SHALL return the same documents from every later identical search.
Source: ASSUMED (ASM-02)   |   Readiness: NEEDS-CLARIFICATION (Q-02)
Acceptance criteria:
- FR-03-AC1: a result list from search has a fake document appended → a second identical search returns only the original document.
- FR-03-AC2: a result served from the cache is cleared with clear() → a second identical search still returns one document.
Notes: both pass on the current code. The criteria only check the list. They do not cover documents inside it (see FR-01 and FR-02).

## 6. Non-functional requirements
None identified.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | Existing tests must not be weakened or deleted (team rule for this run). | STATED (run instructions) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | None identified | — | — |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Copying documents on every search costs memory and time for large tables. | Fix for S2 (Q-01) | Slower repeated searches | Measure after the decision in Q-01. |

Escalation: CNF-01 needs a maintainer decision before FR-01 and FR-02 can be built.

## 10. External evidence log
None identified. No external law, standard or product fact is used.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S2, S4) | CNF-01, Q-01 | BLOCKED |
| FR-02 | ACT-01 | STATED (S2, S4) | CNF-01, Q-01 | BLOCKED |
| FR-03 | ACT-01 | ASSUMED (ASM-02) | Q-02 | NEEDS-CLARIFICATION |
| ACT-01 | — | STATED (S2) | — | — |
| CON-01 | — | STATED (run instructions) | — | — |

## 12. Change log
- 0.1 (2026-11-22): first draft from issue #2. Conflict CNF-01 recorded. No stakeholder answers.

### Open questions
- Q-01 (P1): Should `search()` return independent copies of documents (the issue's expectation, which breaks the existing test `test_query_cache_documents_are_shared_with_cache`), or keep sharing and document it? Options: (a) copy and update that test; (b) keep sharing and close the issue. Blocks FR-01, FR-02. Ask: maintainer.
- Q-02 (P3): Should a caller be allowed to change the returned list without affecting later searches? Blocks FR-03 only.

### Assumptions
- ASM-01: "stored data" means the data in the storage backend as of the last write. Unconfirmed. Affects FR-01, FR-02.
- ASM-02: The list returned by `search()` should not be shared with later searches. Unconfirmed. Affects FR-03.

### Conflicts
- CNF-01: Statement A (S2, S4, issue #2): mutating a returned document must not change later searches. Statement B (tests/test_tinydb.py:732, `test_query_cache_documents_are_shared_with_cache`): the nested mutation of a returned document must change later searches (sharing is intended, and the `search()` docstring says so). Affects FR-01, FR-02. Who decides: maintainer (Q-01).