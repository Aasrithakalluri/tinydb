# Requirements Specification: tinydb search results shared with the query cache
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

| ID | Speaker | Text |
|---|---|---|
| S1 | Issue reporter (GitHub issue #2) | Title: "Modifying a document I got from `search()` changes what later searches return" |
| S2 | Issue reporter | "I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file." |
| S3 | Issue reporter | "If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong." |
| S4 | Issue reporter | "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result." |
| S5 | Issue reporter | Code example: `db = TinyDB('db.json')`; `db.insert({'name': 'a', 'tags': ['x']})`; `q = where('name') == 'a'`; `rows = db.search(q)`; `rows[0]['name'] = 'CHANGED'`; `rows[0]['tags'].append('oops')`; `print(db.search(q))` gives `[{'name': 'CHANGED', 'tags': ['x', 'oops']}]` while the file still holds `'a'` / `['x']`. |

No stakeholder was available to answer questions. Stakeholder availability: none.

## 2. Purpose and scope

**In scope**
- Documents returned by `Table.search()` (and therefore `TinyDB.search()`) when the same query is run again in the same process. Source: STATED (S4, S5).
- Protection of the stored data from changes made to returned documents. Source: STATED (S4, S5).

**Out of scope**
- Other read methods (`all()`, `get()`, `contains()`). Source: ASSUMED (ASM-02). The issue names only `search()`.
- Any change to the on-disk file format. Source: STATED (S3 says the file is correct).
- Performance targets for copying. Source: OPEN (Q-04).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| search result | S5 | The list of documents returned by `search(cond)`. | Defined | None |
| mutate (tweak) | S2, S5 | Change a top-level key, a nested dict value, or a list item of a returned document. | Defined | None |
| stored data | S3, S4 | (a) Data persisted in the storage file at the last write. (b) Data the Table holds in memory after the last write. These coincide only if no returned document shares objects with memory. | AMBIGUOUS | Q-03 |
| same query | S4 | (a) An equal query expression, such as `where('name') == 'a'` built twice. (b) The same query object. | AMBIGUOUS | Q-05 |
| correct data | S3 | Same as "stored data". | AMBIGUOUS | Q-03 |

### Open questions referenced in this specification

- **Q-01 (P1)**: Which contract should `search()` follow? (a) Results are independent copies; the `Table.search` docstring and `test_query_cache_documents_are_shared_with_cache` change. (b) Results stay shared with the cache; the issue is closed by documentation (read-only results). Blocks FR-01, FR-02, FR-03. Ask: repository maintainer. Status: OPEN.
- **Q-02 (P2)**: If copies are chosen, must the copy be deep (nested dicts and lists copied), or is a top-level copy enough? The issue's example mutates a nested list, so this spec assumes deep (ASM-01). Blocks FR-01, FR-02. Ask: maintainer. Status: OPEN.
- **Q-03 (P2)**: Does "stored data" mean the file contents, the in-memory table, or both? Must the guarantee also hold for `MemoryStorage` and custom storage classes? Blocks FR-03. Ask: maintainer. Status: OPEN.
- **Q-04 (P3)**: What maximum extra time per `search()` call is acceptable for copying? Blocks no FR yet; affects RSK-01. Ask: maintainer. Status: OPEN.
- **Q-05 (P3)**: For "same query", is an equal-but-new query expression a cache hit under the required guarantee? Blocks FR-02 wording only. Ask: reporter or maintainer. Status: OPEN.

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Calls `search()`, changes the returned dicts for display, and runs the same query again. | STATED (S2) |
| ACT-02 | Repository maintainer | Decides the result contract (Q-01). Has no FR of its own. This actor is needed to decide Q-01, which blocks the FRs. | INFERRED (from CNF-01: the authority over the documented contract is needed) |

## 5. Functional requirements

### FR-01: First search returns documents isolated from the cache
Actor: ACT-01
Statement: WHEN `search(cond)` is called and `cond` has no cache entry, the system SHALL return documents that share no mutable objects (dicts, lists, nested values) with the cache entry or with any other returned result.
Source: STATED (S4, S5) | Readiness: BLOCKED (CNF-01, Q-01, Q-02)
Acceptance criteria:
- FR-01-AC1: a table holds `{'name': 'a', 'tags': ['x']}` in a JSON file; `r = db.search(q)` is the first call for `q` (cache miss); `r[0]['name'] = 'CHANGED'` and `r[0]['tags'].append('oops')` → `db.search(q)` returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-01-AC2 (nested boundary): a table holds `{'meta': {'k': ['v']}}`; first `r = db.search(q)` (cache miss); `r[0]['meta']['k'].append('z')` → `db.search(q)[0]['meta']['k']` equals `['v']`.
- FR-01-AC3 (multiple matches): the first search returns two matching documents; only `r[0]` is mutated → the next `db.search(q)` returns both documents with their stored values, including the unmodified `r[1]`.
- FR-01-AC4 (no match): the first search for a query that matches nothing returns `[]`; `r.append({'x': 1})` → `db.search(q)` returns `[]`.

Notes: The current code stores `docs[:]` in the cache (tinydb/table.py line 295) and returns `docs` (line 297). Both hold the same document objects (EV-01). A fix to the hit path alone would leave the issue's exact scenario broken (RSK-03). This FR contradicts the current docstring of `Table.search` (tinydb/table.py lines 253–257) and the current test (tests/test_tinydb.py lines 732–753), see CNF-01.

### FR-02: Repeated search returns stored values regardless of earlier mutation
Actor: ACT-01
Statement: WHEN `search(cond)` is called and `cond` has a cache entry, the system SHALL return documents whose values equal the stored data, regardless of any earlier mutation of documents or lists returned by `search()`.
Source: STATED (S4) | Readiness: BLOCKED (CNF-01, Q-01, Q-02, Q-05)
Acceptance criteria:
- FR-02-AC1: after the FR-01-AC1 sequence, a third `db.search(q)` (cache hit) returns `[{'name': 'a', 'tags': ['x']}]`; then mutate that result's `tags` list → the next `db.search(q)` still returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-02-AC2 (list-level boundary): `r = db.search(q)` followed by `r.append({'name': 'fake'})` → the next `db.search(q)` returns only the stored matching documents, and its length equals the count of matching stored documents.
- FR-02-AC3 (failure after write): after a cache hit and a mutation, `db.insert({'name': 'a', 'tags': ['y']})` followed by `db.search(q)` → returns two documents with the stored values `['x']` and `['y']`, and neither contains `'CHANGED'` or `'oops'`.

Notes: The current hit path returns `cached_results[:]` (line 267), a shallow list copy whose documents are the cached objects. This is the path the issue's second search takes.

### FR-03: Mutating search results leaves the stored data unchanged
Actor: ACT-01
Statement: WHEN a caller mutates any document returned by `search()`, the system SHALL leave the stored data unchanged in the storage and in later reads from the same table.
Source: STATED (S3, S4, S5) | Readiness: BLOCKED (CNF-01, Q-01, Q-03)
Acceptance criteria:
- FR-03-AC1: a JSON-backed table holds `{'name': 'a', 'tags': ['x']}`; `r = db.search(q)`; `r[0]['tags'].append('oops')` → the JSON file at `tmp_path` parsed by `json.load` has `_default` equal to `{"1": {"name": "a", "tags": ["x"]}}`.
- FR-03-AC2: the same mutation → `db.all()` returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-03-AC3 (boundary, empty result): `r = db.search(q_no_match)`; `r.append({'name': 'b'})` → `db.all()` returns the same documents as before, and the file's `_default` table has the same number of entries.

Notes: The reporter says the file is correct after a restart (S3). This FR covers the file and in-process reads. Whether `MemoryStorage` behaves the same is UNVERIFIED (Q-03).

## 6. Non-functional requirements

None identified. A performance limit on copying is TBD (Q-04); see RSK-01.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | The input states no constraints. | None |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| None identified | The input names no external system or service. | None | None |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Copying each result (deep copy) makes `search()` slower on large tables. | Q-04 (no threshold stated) | Slower queries for users with large tables; no agreed limit to test against. | Decide the threshold (Q-04); measure before and after the change. |
| RSK-02 | Changing the contract requires changing the existing docstring and test. A rewritten test could hide the defect. | CNF-01 | A test that only checks cache hits passes while the first-search bug remains. | Maintainer approves the contract change (Q-01); the new test must mutate the first (miss) result, as FR-01-AC1 requires. |
| RSK-03 | Fixing only the cache-hit path leaves the issue's exact scenario broken. | FR-01, EV-01 | The reported problem persists on the first search. | Apply the fix to both paths (FR-01 and FR-02). |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| EV-01 | Does the local code return document objects shared with the cache on the miss and hit paths? | Local: tinydb/table.py lines 265–297 (repository working tree; no external URL) | 2026-11-22 | Hit path returns `cached_results[:]` (shallow list copy). Miss path stores `docs[:]` in the cache and returns `docs`. Both share document objects. The docstring (lines 253–257) documents this sharing as intended. Reading only; the reproduction in S5 was not executed. | SUPPORTS (reading of the code agrees with the issue's behaviour) | FR-01, FR-02, FR-03, RSK-03 | Added the notes in FR-01 and FR-02. No label was raised to CONFIRMED. |

No web or fetch call was made. No law, standard, product capability or numeric claim about the outside world is used.

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S4, S5) | CNF-01, Q-01, Q-02, EV-01, RSK-03 | BLOCKED |
| FR-02 | ACT-01 | STATED (S4) | CNF-01, Q-01, Q-02, Q-05, EV-01 | BLOCKED |
| FR-03 | ACT-01 | STATED (S3, S4, S5) | CNF-01, Q-01, Q-03 | BLOCKED |
| ACT-01 | n/a | STATED (S2) | FR-01, FR-02, FR-03 | Not applicable |
| ACT-02 | n/a | INFERRED | Q-01, CNF-01 (no FR; needed to decide Q-01) | Not applicable |
| ASM-01 (deep copy) | ACT-01 | ASSUMED | Q-02, FR-01, FR-02 | Not applicable |
| ASM-02 (scope limited to `search()`) | ACT-01 | ASSUMED | Q-05 (scope) | Not applicable |
| CNF-01 | ACT-02 | Issue S4 vs. repository docstring and test | Q-01 | Not applicable |
| RSK-01 to RSK-03 | n/a | Q-04, CNF-01, EV-01 | see Section 9 | Not applicable |

### Assumptions

- **ASM-01**: Results are deep copies of stored documents, including nested dicts and lists. Basis: S4 ("no matter what I did") and the nested mutation in S5. Affects FR-01, FR-02. Risk if wrong: the contract is a top-level copy, and the FR wording changes. Status: Unconfirmed.
- **ASM-02**: Scope is `search()` only. Basis: S1 and S2 name only `search()`. Affects scope in Section 2. Risk if wrong: `all()`, `get()` or `contains()` carry the same defect. Status: Unconfirmed.

### Conflicts

- **CNF-01**: Statement A (S4, issue reporter): "I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result." Statement B (`Table.search` docstring, tinydb/table.py lines 253–257, and test `test_query_cache_documents_are_shared_with_cache`, tests/test_tinydb.py lines 732–753): results are the same objects held by the cache, to be treated as read-only; the test asserts that mutating a nested value reaches the cache. Affects FR-01, FR-02, FR-03. Who decides: repository maintainer (not identified in the input). Status: OPEN. Readiness effect: BLOCKED.

### Unverified claims

None identified. No external fact is relied on.

### Escalations

- Q-01 (P1) needs a decision from the repository maintainer on the result contract. Until that decision is made, FR-01, FR-02 and FR-03 stay BLOCKED.

## 12. Change log

- **0.1 (2026-11-22)**: Initial draft from GitHub issue #2. No stakeholder answers. Code reading of tinydb/table.py and tests/test_tinydb.py (EV-01). The reproduction in S5 was not run. Overall readiness: NOT READY (P1 question Q-01 open; no FR is READY).