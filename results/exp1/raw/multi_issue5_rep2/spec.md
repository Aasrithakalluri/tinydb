# Requirements Specification: TinyDB Issue #5 (Result Ordering in `all()` and `search()`)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY (P1 question Q-01 is open)

## 1. Input record

Source: GitHub issue #5, Aasrithakalluri/tinydb. Speaker for all sentences: the issue reporter (name and role unknown). No stakeholder is available to answer questions in this run.

- S1: "Results come back in a strange order" (issue title).
- S2: "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right."
- S3: "I don't know exactly when it happens, but it seems related to how I created or changed the documents."
- S4: "It also looks different after I close and reopen the program."
- S5: "I'd like the order to be sensible and predictable, so my page doesn't jump around."

Repository observations (read-only, not external evidence; used only to frame ASM and RSK items):
- `tinydb/table.py:770`: new document IDs are the maximum existing integer ID plus 1.
- `tinydb/table.py:235-247` and `tinydb/table.py:732-742`: `all()` and iteration follow the order of the stored table dictionary.
- `tinydb/table.py:249-297`: `search()` filters that same order and caches results.
- `tinydb/storages.py:147`: `JSONStorage.write` calls `json.dumps(data, **self.kwargs)`.

## 2. Purpose and scope

**In scope**
- The order of documents returned by `Table.all()`, `Table.search()` and iteration over a table, in the TinyDB Python API. Source: S2, S5.
- The order after a database file is closed and reopened with the JSON storage. Source: S4 (INFERRED that the reporter uses persistent storage; see DEP-01).

**Out of scope**
- Sorting by a field chosen by the application. Source: ASSUMED (ASM-03). Option (c) in Q-01.
- Changes to the stored file format beyond key order. Source: ASSUMED (ASM-03).
- This specification does not design code or architecture.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "sensible" (S5) | S5 | Options: (a) ascending document ID; (b) insertion order; (c) order of last change; (d) order by a field. | AMBIGUOUS | Q-01 |
| "predictable" (S5) | S5 | Options: (a) same order on every call; (b) same order after reopen; (c) both. | AMBIGUOUS | Q-01 |
| "strange order" / "doesn't look right" (S1, S2) | S1, S2 | No reference order is stated. The expected order is unknown. | AMBIGUOUS | Q-01 |
| "how I created or changed" (S3) | S3 | Could mean insert, insert_multiple, update, upsert or remove. | AMBIGUOUS | Q-01 |
| "page" (S5) | S5 | Options: (a) an application UI page; (b) one query result; (c) a slice of results. | AMBIGUOUS | Q-01 |
| "close and reopen" (S4) | S4 | Assumed to mean a JSON-backed TinyDB file opened again from the same path. | AMBIGUOUS | Q-02 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | A person or program that calls TinyDB's `all()`, `search()` and iteration on a table. | INFERRED (S2: the reporter calls `db.all()` and `db.search(...)`) |

## 5. Functional requirements

### FR-01: Documents are returned in ascending document ID order
Actor: ACT-01
Statement: WHEN `all()` or iteration over a table is called, the system SHALL return the table's documents in ascending order of their numeric document ID.
Source: ASSUMED (ASM-01, interpretation of S5)   |   Readiness: NEEDS-CLARIFICATION (Q-01 P1; ASM-01)
Acceptance criteria:
- FR-01-AC1: a table with three documents inserted with automatically assigned IDs 1, 2, 3 → `all()` returns doc_ids [1, 2, 3] in that order, and `list(table)` returns the same doc_ids in the same order.
- FR-01-AC2: 12 documents inserted with IDs 1 to 12 → `all()` returns doc_ids [1, 2, 3, ..., 12], not the string order [1, 10, 11, 12, 2, ...].
- FR-01-AC3: documents 1, 2, 3 exist, document 2 is removed with `remove(doc_ids=[2])`, and one new document is inserted → `all()` returns doc_ids [1, 3, 4].
- FR-01-AC4: documents 1, 2, 3 exist and `update({'v': 9}, doc_ids=[1])` is called → `all()` returns doc_ids [1, 2, 3], with document 1 still first.
- FR-01-AC5: a table with no documents → `all()` returns an empty list.

Notes: Under ASM-01, order depends only on document IDs, so updates do not move documents (ASM-02). FR-01-AC3 avoids ID reuse. Repository observation (table.py:770): removing the highest ID and then inserting reuses that ID, which is a boundary case to confirm (Q-05 covers non-integer IDs). Related: Q-01, ASM-01, ASM-02, RSK-02.

### FR-02: Search results keep the same relative order as `all()`
Actor: ACT-01
Statement: WHEN `search(cond)` is called, the system SHALL return the matching documents in the same relative order that `all()` returns them.
Source: ASSUMED (ASM-01 applied to S2)   |   Readiness: NEEDS-CLARIFICATION (Q-01 P1)
Acceptance criteria:
- FR-02-AC1: documents with IDs 1 to 12, each with field `v` equal to its ID, → `search(where('v') >= 2)` returns doc_ids [2, 3, ..., 12] in ascending order.
- FR-02-AC2: the same `search` call is run twice with no write in between → both calls return identical doc_id lists.
- FR-02-AC3: after `update` changes field `tag` on documents 2 and 5 to 'x' → `search(where('tag') == 'x')` returns doc_ids [2, 5].
- FR-02-AC4: no document matches the condition → `search(...)` returns an empty list.

Notes: FR-02-AC2 checks the query cache (table.py:263-297). Related: Q-01, ASM-01.

### FR-03: Order is unchanged after close and reopen
Actor: ACT-01
Statement: WHEN a JSON-backed database is closed and then reopened from the same file, the system SHALL return `all()` and `search()` results in the same order as before the close.
Source: INFERRED (S4: the order changes after reopen, so the expected behaviour is that it stays the same)   |   Readiness: NEEDS-CLARIFICATION (Q-01 P1; Q-02 P2; Q-03 P2; Q-04 P2)
Acceptance criteria:
- FR-03-AC1: a JSON database opened with default options, 12 documents inserted with IDs 1 to 12, then closed and reopened from the same path → `all()` returns doc_ids [1, 2, ..., 12] and `search(where('v') >= 2)` returns doc_ids [2, ..., 12].
- FR-03-AC2: the same database opened with `sort_keys=True`, 12 documents inserted, then closed and reopened → `all()` returns doc_ids [1, 2, ..., 12] and not the string order [1, 10, 11, 12, 2, ...].
- FR-03-AC3: a JSON database file that contains no documents, opened → `all()` returns an empty list.
- FR-03-AC4: a JSON database with one update and one removal, closed and reopened → the `all()` doc_id list after reopen equals the list before the close.

Notes: Repository observation (storages.py:147): `sort_keys=True` is passed to `json.dumps`, which would sort the string keys lexically. This is a plausible cause of S4, but it is not confirmed. See RSK-01, Q-03 and Q-04. The expected result in FR-03-AC2 follows ASM-01 and is not yet confirmed.

## 6. Non-functional requirements

None identified. S1 to S5 do not state a measurable quality (no speed, scale or availability target).

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | No constraint is stated in S1 to S5. | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | A persistent JSON file at a path that can be reopened (needed for FR-03). | INFERRED (S4) | If the reporter uses another storage, FR-03 changes or does not apply (Q-02). |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | With `sort_keys=True`, JSON keys are written and read in lexical order (1, 10, 11, 2, ...), so the order changes after reopen. | S4; repository storages.py:147; Q-03, Q-04 | The reported symptom persists after reopen. | Resolve Q-03; add FR-03-AC2 and FR-03-AC1 as tests. |
| RSK-02 | The intended order may not be ascending ID (for example, last-changed or field-based order). | S5; Q-01 | FR-01 to FR-03 would need rewriting. | Resolve Q-01 before implementation. |
| RSK-03 | A custom storage may not keep key order, so FR-03 cannot be verified for it. | Q-02, Q-03 | FR-03 is untestable for that storage. | Confirm the storage type (Q-02). |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None identified | No external fact is needed. The issue has no law, standard, named product or numeric claim about the outside world. | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | ASSUMED (ASM-01; S5) | Q-01 (P1), ASM-01, ASM-02, RSK-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | ASSUMED (ASM-01; S2) | Q-01 (P1), ASM-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | INFERRED (S4) | Q-01 (P1), Q-02, Q-03, Q-04, RSK-01, RSK-03 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S2) | — | — |
| DEP-01 | — | INFERRED (S4) | Q-02 | — |
| ASM-01 | — | ASSUMED | Q-01 | Unconfirmed |
| ASM-02 | — | ASSUMED | FR-01-AC4 | Unconfirmed |
| ASM-03 | — | ASSUMED | Q-01 | Unconfirmed |
| Q-01 … Q-05 | — | OPEN | — | OPEN |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial draft from issue #5. Interpretation ASSUMED as ascending document ID order. Questions Q-01 to Q-05 open. No stakeholder answers. No external evidence used. |

### Open questions (resolve in this order)

- **Q-01 (P1), blocks FR-01, FR-02, FR-03.** What order is intended by "sensible and predictable"? Options: (a) ascending document ID (ASM-01); (b) order of last insert or change; (c) order by a field chosen by the application. Ask: the issue reporter.
- **Q-02 (P2), blocks FR-03 and DEP-01.** Which storage is used: default JSON storage, a custom storage or in-memory storage? Ask: the issue reporter.
- **Q-03 (P2), blocks FR-03-AC2 and RSK-01.** If `sort_keys=True` is set, should results still be in ascending ID order (a), or should the file's key order decide (b)? Ask: maintainers.
- **Q-04 (P2), blocks FR-03-AC1.** With default JSON options, do document IDs keep their insertion order after reopen? Confirm by test. Ask: maintainers.
- **Q-05 (P3), detail.** For a custom `document_id_class` whose IDs are not integers, should ordering use the raw key? Ask: maintainers.