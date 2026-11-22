# Requirements Specification: tinydb, issue #2 (search() results share objects with the query cache)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

| S# | Speaker | Text |
|---|---|---|
| S1 | Issue reporter (unnamed user) | Title: "Modifying a document I got from `search()` changes what later searches return." |
| S2 | Issue reporter | "I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file." |
| S3 | Issue reporter | Code example: `db = TinyDB('db.json')`; `db.insert({'name': 'a', 'tags': ['x']})`; `q = where('name') == 'a'`; `rows = db.search(q)`; `rows[0]['name'] = 'CHANGED'`; `rows[0]['tags'].append('oops')`; `print(db.search(q))` prints `[{'name': 'CHANGED', 'tags': ['x', 'oops']}]` while the file still holds `'a'` / `['x']`. |
| S4 | Issue reporter | "If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong." |
| S5 | Issue reporter | "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result." |

Stakeholders available to answer: none. The maintainer is not present in this pipeline, so all questions stay open.

## 2. Purpose and scope

**Problem (STATED S1, S2, S5):** within one process, mutating a document returned by `Table.search()` changes the results of a later identical `search()`.

**In scope:**
- Results returned by `search()` for a repeated query in one process (STATED S5).
- Mutations of returned documents, both top-level keys and nested values (STATED S3).
- Interaction of the result with later writes through `insert()`, `update()` and `remove()` (INFERRED from S5: "the stored data" must be current after writes).

**Out of scope:**
- The on-disk file format and persistence. Reason: S4 says the file is correct. (INFERRED)
- Query-cache capacity and eviction policy. Reason: not raised in the issue. (INFERRED)

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "stored data" | S5 | (a) the documents in the table as of the last write; (b) the contents of the file on disk. S4 treats them as equal in a fresh process. | AMBIGUOUS | Q-01 |
| "copy" of a result | S5 (implied) | (a) shallow copy of each document (top-level keys only); (b) deep copy (nested values too); (c) read-only view that raises on mutation. | AMBIGUOUS | Q-01 |
| "the same query" | S5 | Equal `QueryLike` objects that hit the same cache key. Options: same object only, or same hash. | AMBIGUOUS | Q-04 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Python application developer | Uses TinyDB in-process, calls `search()`, and modifies returned dicts for display (S2, S3). | STATED (S2, S3) |

## 5. Functional requirements

### FR-01: Results of search() are isolated from the query cache
Actor: ACT-01
Statement: WHEN ACT-01 modifies a document returned by `search()` (top-level keys or nested values), the system SHALL return the stored document unchanged from every later `search()` with an equal query, for as long as no write has occurred.
Source: ASSUMED (ASM-01, based on S5) | Readiness: BLOCKED (CNF-01, Q-01, Q-02)
Acceptance criteria:
- FR-01-AC1: table holds `{'name': 'a', 'tags': ['x']}`; `rows = db.search(q)` with `q = where('name') == 'a'`; `rows[0]['name'] = 'CHANGED'` → second `db.search(q)` returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-01-AC2: same table; `rows[0]['tags'].append('oops')` → second `db.search(q)` returns a document whose `tags` equals `['x']`.
- FR-01-AC3 (boundary, cache miss): `q` has never been searched before in this process; `rows = db.search(q)` is mutated as in FR-01-AC1 → a later `db.search(q)`, served from the cache, returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-01-AC4 (boundary, result list): `rows.append({'name': 'fake'})` → a later `db.search(q)` returns only the stored matching documents (one entry).
- FR-01-AC5 (failure, write after mutation): `rows[0]['name'] = 'CHANGED'`, then `db.update({'name': 'b'}, where('name') == 'a')` → `db.search(where('name') == 'b')` returns `[{'name': 'b', 'tags': ['x']}]`.

Notes: Conflicts with the current docstring of `Table.search()` in `tinydb/table.py` (lines 253–257), which states that returned documents are shared with the cache and that mutating them corrupts later identical searches. See CNF-01. The existing test `test_query_cache_documents_are_shared_with_cache` in `tests/test_tinydb.py` (line 732) only mutates the returned list, not the documents, so it does not contradict FR-01-AC4. Readiness stays BLOCKED until a maintainer decides the contract (Q-01). Current code on a cache miss (`self._query_cache[cond] = docs[:]`) stores the same document objects that are returned, so FR-01-AC3 describes a defect in the present code as well.

### FR-02: Writes remain visible to later identical searches
Actor: ACT-01
Statement: WHEN a document is inserted, updated or removed after a `search()`, the system SHALL return the post-write stored data from the next `search()` with an equal query.
Source: INFERRED (from S5; needs confirmation) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: `db.search(q)` returns 1 document; `db.insert({'name': 'a', 'tags': []})` → next `db.search(q)` returns 2 documents.
- FR-02-AC2 (boundary): `db.search(q)` is cached; `db.update({'name': 'z'}, where('name') == 'a')` → next `db.search(q)` returns `[]`.
- FR-02-AC3 (failure): `db.search(q)` is cached; `db.remove(where('name') == 'a')` → next `db.search(q)` returns `[]`.
- FR-02-AC4 (write after mutation): a returned document is mutated to `'CHANGED'`; `db.insert({'name': 'c', 'tags': []})` → `db.search(where('name') == 'a')` returns `[{'name': 'a', 'tags': ['x']}]` (stored value, not the mutated one).

Notes: Relies on the existing cache clear that runs on writes (`clear_cache()` at `tinydb/table.py` line 854). Readiness depends on the contract chosen under Q-01.

## 6. Non-functional requirements

None identified. The cost of copying on every search is unmeasured. See Q-03 and RSK-01. No metric or threshold is written, so no NFR block is created.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | No external constraint (time, budget, platform, law) was stated in the issue. | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| None identified | The issue names no external system, service or team. | — | — |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Copying every returned document on every search, including cache hits, increases CPU and memory use for large results. | Q-03 | Slower repeated searches on large tables. | Decide the acceptable cost (Q-03), then measure it. |
| RSK-02 | Changing `search()` to return copies breaks users who rely on the documented shared-object behaviour. | CNF-01 | Behaviour change for existing code. | Maintainer decision (Q-01); document the change in the changelog. |
| RSK-03 | A fix limited to the cache-hit path leaves the cache-miss path (FR-01-AC3) broken. | Q-02 | The reported bug persists for the first search of a query. | Apply the fix to both paths; test both (FR-01-AC3). |

## 10. External evidence log

No external evidence was needed. The issue names no law, standard, product or service, and no numeric claim about the outside world. Repository reading (`tinydb/table.py`, `tests/test_tinydb.py`) was used to understand current behaviour and is recorded in Section 5 notes and CNF-01, not as EV entries.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None identified | — | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| ACT-01 | — | STATED (S2, S3) | — | READY (actor only) |
| FR-01 | ACT-01 | ASSUMED (ASM-01, from S5) | Q-01, Q-02, Q-04, CNF-01, RSK-02, RSK-03 | BLOCKED |
| FR-02 | ACT-01 | INFERRED (from S5) | Q-01, RSK-01 | NEEDS-CLARIFICATION |
| Q-01 (contract) | — | OPEN | blocks FR-01, FR-02 | — |
| Q-02 (miss path) | — | OPEN | blocks FR-01-AC3 | — |
| Q-03 (cost) | — | OPEN | RSK-01 | — |
| Q-04 (query identity) | — | OPEN | blocks FR-01 scope | — |
| CNF-01 | — | STATED (S5) vs repository docstring | blocks FR-01 | — |
| ASM-01, ASM-02 | — | ASSUMED | FR-01, FR-02 | — |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from issue #2. Two requirements drafted (FR-01 BLOCKED, FR-02 NEEDS-CLARIFICATION). Questions Q-01 to Q-04 open. |