# Requirements Specification: tinydb search result isolation
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY (no requirement is READY; FR-01 is BLOCKED by CNF-01)

## 1. Input record
- S1 (issue author, unnamed reporter): "I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file."
- S2 (issue author): "If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong."
- S3 (issue author): "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result."
- Stakeholders available to answer: none. Decisions are recorded as open.

## 2. Purpose and scope
- In scope: a document returned by `Table.search()` changed by the caller must not change what later `search()` calls of the same query return, or what storage holds. Source: STATED (S1, S3).
- In scope: writes (`update`, `remove`) still show their effect on later searches. Source: INFERRED (ARCHITECTURE.md constraint 5, every change clears the query cache).
- Out of scope: performance targets for the copy, changes to the storage interface, changes to the query hash, and the on-disk file format. Source: ASSUMED (ASM-01), since the issue names none of these.
- Software problem: yes (Python library API).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| stored data | S2, S3 | (a) what the storage's read() returns; (b) what is written to the file on disk. For in-memory storage these differ. | AMBIGUOUS | Q-04 |
| search result | S3 | the list returned by `Table.search()` | STATED | — |
| no matter what I did | S3 | any mutation of a returned document, including nested values | INFERRED | Q-02 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | Python code that calls `search()` and modifies the returned dicts | INFERRED (S1 "I loaded some documents with `search()`") |

## 5. Functional requirements

### FR-01: Repeated search returns stored data after a modified result
Actor: ACT-01
Statement: WHEN the same query is searched again in one process, the system SHALL return the stored document values regardless of changes the caller made to an earlier result.
Source: STATED (S3) | Readiness: BLOCKED (CNF-01)
Acceptance criteria:
- FR-01-AC1: the query is searched twice, the second result has its top-level value and its nested list changed, and the query is searched a third time → the third result equals the originally stored document.
- FR-01-AC2: a query with no matching documents is searched twice, a dict is appended to the second result, and the query is searched a third time → the third result is an empty list.
- FR-01-AC3: a query served from the cache is searched twice → the two returned lists are different objects and their first documents are different objects.
Notes: Blocked until the maintainer decides CNF-01. The issue reporter's expectation (S3) is applied.

### FR-02: Modifying the first, uncached result does not reach storage or later searches
Actor: ACT-01
Statement: IF the caller modifies a search result before the query has been cached, THEN the system SHALL keep the stored data and all later search results unchanged.
Source: INFERRED (S3 "no matter what I did to the previous result"; "previous" covers the first search too) | Readiness: NEEDS-CLARIFICATION (Q-02)
Acceptance criteria:
- FR-02-AC1: the query is searched once, a value is appended to the nested list of its result, and the query is searched again → the second result has the original nested list.
- FR-02-AC2: a search result has its top-level and nested values changed → the raw storage read of the table still holds the original document values.
- FR-02-AC3: a query built with `map()` (not cacheable) is searched and its result is changed, and the query is searched again → the second result holds the stored values and the query cache holds no entries.
Notes: Storage isolation for the first search is inferred, not stated.

### FR-03: Writes after a modified result show the updated stored data
Actor: ACT-01
Statement: WHEN a matching document is updated or removed after a search result was modified, the system SHALL return the updated or removed stored data on the next search.
Source: INFERRED (ARCHITECTURE.md constraint 5: every table change clears the cache) | Readiness: NEEDS-CLARIFICATION (Q-03)
Acceptance criteria:
- FR-03-AC1: a search result is changed, the matching document is updated from name "a" to "b", and the query for "b" is searched → the result holds the document with name "b" and the original query for "a" returns an empty list.
- FR-03-AC2: a search result is changed and the matching document is removed → the next search of the same query returns an empty list.
Notes: Behaviour is unchanged from the existing write path; only the isolation is new.

## 6. Non-functional requirements
None identified. A performance limit on the copy made per cache hit is not specified: TBD (Q-01).

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | No runtime dependencies; standard library only | STATED (ARCHITECTURE.md section 0 and pyproject.toml) |
| CON-02 | Every table change goes through `Table._update_table`, which clears the query cache | STATED (ARCHITECTURE.md section 3, constraint 5) |
| CON-03 | Storage interface stays `read()` / `write()` / `close()` | STATED (ARCHITECTURE.md section 3, constraint 1) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Python standard library `copy` module | INFERRED (needed for deep copies; no third-party package) | None identified |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Copying each document on every cache hit slows large searches | Q-01 | Slower repeated searches | Measure after the change and set an NFR |
| RSK-02 | Values that cannot be deep-copied (e.g. locks) now fail in `search()` | Q-01 | Search raises for such stored values | Confirm whether this case is in scope |
| RSK-03 | ARCHITECTURE.md ADR-3 says cached documents are shared with the caller | CNF-01 | Documentation is wrong after the change | Update the ADR after the decision |

## 10. External evidence log
| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None identified | No external fact is involved; the issue is about this library's own API | — | — | — | — | — | — |

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S3) | CNF-01 | BLOCKED |
| FR-02 | ACT-01 | INFERRED (S3) | Q-02 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | INFERRED (ARCHITECTURE.md) | Q-03 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1) | — | — |
| CON-01..03 | — | STATED (repository docs) | — | — |
| DEP-01 | — | INFERRED | — | — |

## 12. Change log
- 0.1 (2026-11-22): first draft from issue #2. Open questions and assumptions are below.

### Open questions (P-ranked)
- Q-01 (P3): Is a copy on every cache hit acceptable, or is a performance limit wanted? Blocks: NFR-01 (not drafted).
- Q-02 (P2): Should the first, uncached search result also be isolated from storage (FR-02), or only cache hits? Blocks: FR-02.
- Q-03 (P3): Should write behaviour stay exactly as it is? Blocks: FR-03 confirmation.
- Q-04 (P3): Does "stored data" mean the storage's `read()` result or the file on disk? Blocks: none.

### Assumptions
- ASM-01 (Unconfirmed): the fix is to copy documents, not to freeze them or change the storage interface. Risk if wrong: FR-01 and FR-02 change.

### Conflicts
- CNF-01: Statement A (S3): the stored data must be returned regardless of changes to earlier results. Statement B (test `test_query_cache_documents_are_shared_with_cache` in tests/test_tinydb.py and the `Table.search` docstring, both in the repository): documents are shared with the cache and must be treated as read-only. Affects FR-01. Who decides: the maintainer. Status: open.

### Unverified claims
None identified.

### Escalations to a human
- CNF-01: a maintainer must confirm that copy-on-return replaces the documented shared-object behaviour.