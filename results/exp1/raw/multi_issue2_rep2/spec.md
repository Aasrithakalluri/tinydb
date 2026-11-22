# Requirements Specification: tinydb: search() results shared with the query cache
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Speaker: issue reporter (GitHub issue #2 of Aasrithakalluri/tinydb). No stakeholder is available to answer questions.

- S1: "Modifying a document I got from `search()` changes what later searches return."
- S2: "I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file."
- S3: Code sample. `db = TinyDB('db.json')`, `db.insert({'name': 'a', 'tags': ['x']})`, `q = where('name') == 'a'`. The sample mutates `rows[0]['name']` and `rows[0]['tags']` from `db.search(q)`, then calls `db.search(q)` again. The second result is `[{'name': 'CHANGED', 'tags': ['x', 'oops']}]`, while the file still holds `'a'` and `['x']`.
- S4: "If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong."
- S5: "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result."

## 2. Purpose and scope

**In scope**
- Results of repeated `Table.search()` calls within one process, after the caller has changed a previously returned result (S1, S2, S4, S5).

**Out of scope**
- The on-disk file format and write behaviour. S4 states that the file is already correct.
- Changes to what a query matches (S2, S5).

**Unclear scope (see Q-05)**
- Other read methods (`all()`, `get()`) are not mentioned in the input.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "stored data" | S4, S5 | (a) the content of the file on disk; (b) the in-memory table state seen by the same `TinyDB` instance, including unflushed writes under caching middleware | AMBIGUOUS | Q-02 |
| "the same query" | S5 | (a) the same query object; (b) any query with an equal condition, such as `where('name') == 'a'` built twice | AMBIGUOUS | Q-03 |
| "no matter what I did to the previous result" | S5 | Absolute. Covers top-level keys, nested values, and the returned list. Its cost is not bounded (see RSK-01) | AMBIGUOUS | Q-01, Q-04 |
| "tweaked the dicts" | S2 | Any in-place change to a returned document, including nested mutation | AMBIGUOUS (scope only) | Q-01 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | A Python program that uses tinydb's `TinyDB`, `search()` and query API and changes returned dicts (S2, S3). | STATED (S2) |

## 5. Functional requirements

### FR-01: Repeated search returns stored data after the caller changes a previous result
Actor: ACT-01
Statement: WHEN a caller has modified a document returned by `search(cond)`, the system SHALL return the stored data for every later `search(cond)` call on the same table.
Source: STATED (S1, S2, S5) | Readiness: BLOCKED (CNF-01, Q-01 P1)
Acceptance criteria:
- FR-01-AC1: a table contains `{'name': 'a', 'tags': ['x']}`; `rows = search(q)`; then `rows[0]['name'] = 'CHANGED'` and `rows[0]['tags'].append('oops')`; then `search(q)` → returns exactly `[{'name': 'a', 'tags': ['x']}]`.
- FR-01-AC2 (boundary: key added and removed): `rows = search(q)`; then `rows[0]['new_key'] = 1` and `del rows[0]['name']`; then `search(q)` → returns exactly `[{'name': 'a', 'tags': ['x']}]`, with no `new_key` and with `name` present.
- FR-01-AC3 (boundary: list-level change): `rows = search(q)`; then `rows.append({'name': 'a', 'tags': []})`; then `search(q)` → returns a list of length 1 containing the stored document.
- FR-01-AC4 (failure: other read paths and reopen): after FR-01-AC1 is performed, `db.all()` → contains the stored values `{'name': 'a', 'tags': ['x']}` for that document, and a new `TinyDB('db.json')` instance running `search(q)` → returns the same stored values.
- FR-01-AC5 (failure: no match): `rows = search(q)` where no document matches, then `rows.append({})`; then `search(q)` → returns `[]`.

Notes: CNF-01 is open. The `search()` docstring (tinydb/table.py:253-257) tells callers to treat results as read-only, which conflicts with S5. Under the other choice in Q-01 (callers must not mutate results, as documented), FR-01-AC1 to AC3 would become a documentation requirement and not a test. Related: EV-01, ASM-01, Q-01, Q-02, Q-03, Q-04, RSK-01, RSK-02.

### FR-02: Other read methods return stored data after a caller changes a search result
Actor: ACT-01
Statement: WHEN a caller has modified a document returned by `search(cond)`, the system SHALL return the stored data from `all()` and `get()` on the same table.
Source: INFERRED (S1 and S2 name only `search()`; the caller's concern is the stored data) | Readiness: NEEDS-CLARIFICATION (Q-05, ASM-02)
Acceptance criteria:
- FR-02-AC1: after `rows = search(q)` and `rows[0]['name'] = 'CHANGED'`, `db.all()` → contains the stored document `{'name': 'a', 'tags': ['x']}` with no `CHANGED` value.
- FR-02-AC2 (boundary: get by id): after the mutation in FR-02-AC1, `db.get(doc_id)` for the stored document's id → returns a dict with `name` equal to `'a'`.

Notes: Whether `all()` and `get()` share objects with the query cache is UNVERIFIED (not checked by running code). Related: ASM-02, Q-05.

## 6. Non-functional requirements

None identified. Performance cost of copying returned documents is OPEN (Q-04); no metric or threshold is set. A future NFR would be written as: TBD (Q-04).

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The stored file content is already correct and is not the subject of this issue. | STATED (S4) |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Storage backend and optional caching middleware that supply `_read_table()` data (JSON storage, `CachingMiddleware`) | INFERRED (tinydb/table.py:779-802 and tinydb/middlewares.py:101-106) | If the backend returns shared in-memory objects, the fix needs changes in the storage path as well as in `search()`. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | "No matter what" (S5) requires isolation from nested changes, which may need a deep copy of every returned document. | S5, Q-01 | Fix may be unbounded in cost, or may be impossible to make complete for arbitrary objects. | Decide the copy scope in Q-01. |
| RSK-02 | Copying results on every search may slow searches on large tables. | Q-04 | Regression for users with large tables. | Set a threshold (Q-04) and measure before and after the change. |
| RSK-03 | Documented read-only contract (tinydb/table.py:253-257) conflicts with the reporter's expectation. | CNF-01 | Changing the behaviour may break callers who rely on the shared objects. | Maintainers decide (Q-01). |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| EV-01 | Does `Table.search()` return objects that the query cache also holds? | Local repository: tinydb/table.py lines 249-297 and 779-802 (no network fetch) | 2026-11-22 | On a cache miss, `search()` builds `Document` objects from `_read_table()` and stores `docs[:]` (a list copy holding the same `Document` objects) in `_query_cache`. On a cache hit it returns `cached_results[:]`, which holds the same objects. `Document` copies only the top level (shallow), so nested values are shared with the table data. Not executed; reading only. | SUPPORTS (code reading only) | FR-01, FR-02, ASM-01 | ASM-01 added. CNF-01 added. FR-01 set to BLOCKED. |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S2, S5) | Q-01 (P1), Q-02, Q-03, Q-04, CNF-01, EV-01, ASM-01, RSK-01, RSK-02 | BLOCKED |
| FR-02 | ACT-01 | INFERRED (S1, S2) | Q-05 (P2), ASM-02, EV-01 | NEEDS-CLARIFICATION |
| ACT-01 | n/a | STATED (S2) | none | n/a |
| CON-01 | n/a | STATED (S4) | none | n/a |
| DEP-01 | n/a | INFERRED (code reading) | EV-01 | n/a |
| CNF-01 | n/a | S5 vs. tinydb/table.py:253-257 | Q-01 | n/a |
| Q-01 to Q-05 | n/a | see Section 1 | see Section 3 | n/a |
| ASM-01, ASM-02 | n/a | see Section 3 | FR-01, FR-02 | n/a |

Q-01 (P1): Which contract applies to documents returned by `search()`? (a) Each result is an independent copy, so caller changes never reach later results (cost: a copy on each search). (b) Results stay shared and callers must not mutate them, as the docstring now says. Blocks FR-01 and FR-02. Ask: tinydb maintainers.
Q-02 (P2): Does "stored data" mean the file on disk, or the in-memory table state of the same `TinyDB` instance, including writes not yet flushed under caching middleware? Blocks FR-01 AC wording. Ask: reporter.
Q-03 (P2): Does "the same query" mean the same query object, or any query with an equal condition built separately? Blocks FR-01 AC1 to AC3. Ask: reporter.
Q-04 (P3): What is the acceptable per-search overhead, for example a maximum percentage slowdown on a stated table size? Blocks the future NFR and RSK-02 threshold. Ask: maintainers.
Q-05 (P2): Should `all()` and `get()` have the same protection as `search()`, or is `search()` the only scope? Blocks FR-02. Ask: maintainers and reporter.

## 12. Change log

- v0.1 (2026-11-22): initial draft from issue #2. Created FR-01 (BLOCKED), FR-02 (NEEDS-CLARIFICATION), ASM-01, ASM-02, CNF-01, EV-01, RSK-01 to RSK-03, and questions Q-01 to Q-05. No external claims were raised. Nothing was run; the findings are from code reading only.