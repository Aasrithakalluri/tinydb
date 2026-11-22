# Requirements Specification: tinydb result ordering (Issue #5)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Speaker for all sentences: issue author (unnamed reporter of Aasrithakalluri/tinydb issue #5). No stakeholder was available to answer questions.

- S1: "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right."
- S2: "I don't know exactly when it happens, but it seems related to how I created or changed the documents."
- S3: "It also looks different after I close and reopen the program."
- S4: "I'd like the order to be sensible and predictable, so my page doesn't jump around."

Mapping: S1 → FR-01, FR-02 (scope of the calls). S2 → FR-02 (create/update/remove). S3 → FR-03 (reopen). S4 → FR-01 to FR-03 (goal; the meaning of "sensible" is OPEN, Q-01).

## 2. Purpose and scope

**In scope**
- Order of documents returned by `Table.all()`, `Table.search(cond)` and iteration over a table (S1, S4). The default table is covered through `TinyDB.all()`/`search()`, which delegate to it (repository read: `tinydb/database.py:270`).
- Order after inserting, updating and removing documents (S2).
- Order after closing and reopening a database file (S3). Reopen is assumed to mean JSON storage at the same path (ASM-04).

**Out of scope**
- `get()` ordering, sort-by-field features, pagination and query-cache design. Source: ASSUMED (ASM-05), because the issue does not mention them.
- Changes to the public API signatures. Source: ASSUMED (ASM-05).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "sensible" order | S4 | (a) ascending doc_id (first-insertion order); (b) most recently modified first; (c) user-chosen sort key | AMBIGUOUS | Q-01 |
| "predictable" | S4 | Same input operations give the same order on every run and after reopen. Interpretation chosen: ASM-01, ASM-03. | AMBIGUOUS | Q-01 |
| "doesn't look right" | S1 | Unspecified. The reporter gives no expected order and no example. | AMBIGUOUS | Q-01 |
| "created or changed" | S2 | Insert, update, remove, or a combination. Interpretation chosen: all three are in scope (FR-02). | AMBIGUOUS | Q-01, Q-03 |
| "reopen" | S3 | (a) new TinyDB object at the same path in the same process; (b) new process. Both are treated as equivalent. | AMBIGUOUS | Q-05 |
| "jump around" | S4 | Relative order of unchanged documents changes between calls. | AMBIGUOUS | Q-01 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer using the tinydb Python API | Calls `db.all()`, `db.search(...)`, updates, removes and reopens a database file. | INFERRED (S1, S3: the reporter calls these methods and reopens the program) |

## 5. Functional requirements

### FR-01: Results are returned in ascending numeric document-ID order
Actor: ACT-01
Statement: WHEN the application calls `all()`, iterates the table, or calls `search(cond)`, the system SHALL return the matching documents in ascending numeric `doc_id` order.
Source: ASSUMED (ASM-01), interpreting S1 and S4 | Readiness: NEEDS-CLARIFICATION (Q-01, P1)
Acceptance criteria:
- FR-01-AC1: a new database at a fresh path, with three documents inserted in one session → `[doc.doc_id for doc in db.all()]` equals `[1, 2, 3]`.
- FR-01-AC2: boundary, 12 documents inserted in one session with IDs 1 to 12 → `all()` returns doc_ids `[1, 2, ..., 12]` (numeric order, not text order such as 1, 10, 11, 2).
- FR-01-AC3: 12 documents with field `v` set to 1 to 12, and `search(where('v') >= 2)` → the returned doc_ids equal `[2, 3, ..., 12]` in that order.
- FR-01-AC4: failure/empty case, a table with no documents → `all()` returns `[]` and `search(where('v') == 1)` returns `[]`.
Notes: The "sensible" order is not confirmed. Alternatives (b) and (c) from Q-01 would replace these criteria. Related: RSK-01, EV-02.

### FR-02: Updates and removals do not reorder other documents
Actor: ACT-01
Statement: WHEN an existing document is updated or another document is removed, the system SHALL keep the relative order of all remaining documents unchanged in `all()` and `search()` results.
Source: ASSUMED (ASM-02), interpreting S2 | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-03 P2)
Acceptance criteria:
- FR-02-AC1: three documents inserted (IDs 1, 2, 3), then `db.update({'v': 9}, doc_ids=[1])` → `all()` doc_ids remain `[1, 2, 3]`.
- FR-02-AC2: boundary, `db.update({'v': 9}, where('v') == 'missing')` matches no document → `all()` doc_ids are identical to the list recorded before the call.
- FR-02-AC3: three documents inserted (IDs 1, 2, 3), `db.remove(doc_ids=[2])`, then one new document inserted → `all()` doc_ids equal `[1, 3, 4]`, and the new document is last. (Assumes the next ID is 4 in the same session; reuse after reopen is OPEN, Q-03.)
- FR-02-AC4: failure case, all documents removed → `all()` returns `[]`, and a later insert gets an ID greater than 0 and appears alone in `all()`.
Notes: Current code assigns IDs through `_get_next_id()` (`tinydb/table.py:744`), which caches the next ID within a session. Whether a removed ID may be reused is OPEN (Q-03).

### FR-03: Order is identical after closing and reopening a JSON database
Actor: ACT-01
Statement: WHEN a JSON-backed database is closed and reopened at the same path, the system SHALL return `all()` and `search(cond)` results in the same document order as before the close.
Source: ASSUMED (ASM-03, ASM-04), interpreting S3 | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-02 P2, Q-05 P3)
Acceptance criteria:
- FR-03-AC1: default `TinyDB(path)`, 12 documents inserted, `all()` doc_ids recorded, database closed, `TinyDB(path)` reopened → `all()` doc_ids equal the recorded list `[1, ..., 12]`.
- FR-03-AC2: boundary, same steps with `TinyDB(path, sort_keys=True)` → `all()` doc_ids equal `[1, ..., 12]` after reopen. (Not verified by running tests; see CLM-01, RSK-02.)
- FR-03-AC3: failure case, before close, one document is updated and one removed from a 12-document database → after reopen, `all()` doc_ids equal the ascending list of the surviving IDs.
Notes: `JSONStorage.write` passes `self.kwargs` to `json.dumps` (`tinydb/storages.py:147`), and the library itself does not sort results (repository read, EV-02). Whether `sort_keys=True` must keep its effect on the file is OPEN (Q-02).

## 6. Non-functional requirements

None identified. S1 to S4 state no measurable quality (no time, size or throughput limit). Deterministic order is covered by FR-03.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | None stated in S1 to S4. Public API signatures are assumed unchanged (ASM-05). | ASSUMED (ASM-05) |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Local file-system storage, using the JSON storage at a path, for reopen. | ASSUMED (ASM-04), interpreting S3 | If the reporter uses a custom storage, FR-03 scope changes (Q-04). |
| DEP-02 | Python standard-library `json` module (`dumps` with `sort_keys`) for file key order. | INFERRED (`tinydb/storages.py:147`) | If key-order behaviour differs from CLM-01, FR-03-AC2 result changes. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Documents with IDs above 9 come back before IDs 2 to 9 after reopen when keys are sorted as text. | S3; CLM-01; EV-02; Q-02 | This is the likely symptom in S3. Results appear to jump. | Confirm with a test (FR-03-AC2) before deciding the fix. |
| RSK-02 | Changing key order for `sort_keys=True` users breaks code that relies on the current file order. | Q-02 | Behaviour change for existing users. | Ask Q-02 before changing the file format. |
| RSK-03 | Custom storages or non-integer `document_id_class` values have no numeric order, so FR-01 cannot be applied directly. | Q-04 | FR-01 scope is incomplete for these cases. | Ask Q-04. |
| RSK-04 | Removed IDs may be reused after reopen (`_get_next_id` restarts from the maximum ID), which changes which document is "last" in the user's mental model. | S2; Q-03 | Possible confusion, not a sorting failure. | Ask Q-03. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| EV-01 | Does Python's `json.dumps(sort_keys=True)` sort dictionary keys as strings, so "10" sorts before "2"? | None (no fetch tool available in this stage) | n/a | Not checked. | INCONCLUSIVE (not run) | CLM-01, FR-03-AC2, RSK-01 | None. CLM-01 stays UNVERIFIED. |
| EV-02 | Does the repository's table code sort results, and does JSON storage pass options to `json.dumps`? | Repository files: `tinydb/table.py` (`all`, `search`, `__iter__`, `_get_next_id`), `tinydb/storages.py:147` | 2026-11-22 | `all()` returns `list(iter(self))`, `search()` iterates `_read_table().items()`, and no sort call exists in `tinydb/`. `JSONStorage.write` calls `json.dumps(data, **self.kwargs)`. Default kwargs are not sorted in library code. | SUPPORTS (order comes from storage mapping order) | FR-01, FR-03, RSK-01 | Used to write FR-01 to FR-03 notes. |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | ASM-01 (S1, S4) | Q-01; EV-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | ASM-02 (S2) | Q-01, Q-03; EV-02 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASM-03, ASM-04 (S3) | Q-01, Q-02, Q-05; CLM-01; EV-02 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S1, S3) | Q-01 | Not a requirement |
| CON-01 | — | ASM-05 | — | Not a requirement |
| DEP-01 | — | ASM-04 (S3) | Q-04 | Not a requirement |
| DEP-02 | — | INFERRED (`storages.py:147`) | CLM-01 | Not a requirement |
| ASM-01 to ASM-05 | — | ASSUMED | See register | Unconfirmed |
| RSK-01 to RSK-04 | — | See Section 9 | Q-02, Q-03, Q-04 | Open |
| CLM-01 | — | Claim from issue analysis about `sort_keys` text order | EV-01 | UNVERIFIED |

**Assumptions (ASM)**
- ASM-01: "Sensible" order means ascending numeric doc_id, that is, first-insertion order (basis: S4; alternatives in Q-01).
- ASM-02: Updates and removals of other documents do not change the relative order of the remaining documents (basis: S2).
- ASM-03: "Predictable" means the same order before and after reopen, with no other changes (basis: S4).
- ASM-04: "Reopen" means a JSON-backed database at the same path (basis: S3).
- ASM-05: Out-of-scope items in Section 2 are not required, and public API signatures do not change (basis: silence in S1 to S4).

**Questions (Q)**
- Q-01 (P1): What order is "sensible" for `all()` and `search()`?
  - (a) ascending doc_id, which is first-insertion order;
  - (b) most recently modified first;
  - (c) order by a field the user chooses.
  - Blocks FR-01, FR-02, FR-03. Ask: issue author.
- Q-02 (P2): When a user passes `sort_keys=True` to JSON storage, must document order follow ascending doc_id (overriding text key order), or must `sort_keys` keep its current effect on the file?
  - Blocks FR-03-AC2, RSK-01, RSK-02. Ask: issue author and maintainers.
- Q-03 (P2): After a removal, may a later insert reuse a removed ID?
  - (a) yes, which is the current behaviour after reopen;
  - (b) never.
  - Blocks FR-02-AC3, RSK-04. Ask: maintainers.
- Q-04 (P2): Does the order rule apply to custom storages and to non-integer `document_id_class` values?
  - (a) JSON and in-memory storage only;
  - (b) all storages, with a text-order fallback for non-numeric IDs.
  - Blocks FR-01 and FR-03 scope, RSK-03. Ask: maintainers.
- Q-05 (P3): Does "reopen" mean a new TinyDB object in the same process, or a new process? Blocks FR-03-AC1 test design only. Ask: issue author.

**Conflicts (CNF)**
- None identified. The issue has one author and no conflicting statements. The tension between "predictable" and `sort_keys=True` is recorded as Q-02 and RSK-01.

**Claims (CLM)**
- CLM-01: Using `sort_keys=True` on JSON storage makes document IDs sort as text (for example 1, 10, 11, 2), which changes the order after reopen. Status: UNVERIFIED. EV-01 was not run. Repository evidence (EV-02) supports the mechanism but does not confirm the output.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | First draft from Issue #5 (S1 to S4). Three FRs, five assumptions, five questions, four risks, one claim. Readiness: all FRs NEEDS-CLARIFICATION because Q-01 (P1) is open. |

## Check summary (not a separate file)

- Readiness: 0 READY, 3 NEEDS-CLARIFICATION, 0 BLOCKED. Overall NOT READY because P1 question Q-01 is open.
- Tool use: the repository was read (Grep and Read). No fetch call was made because the issue names no law, standard or product; the Python `json` behaviour (CLM-01) was not checked because no fetch tool is available in this stage (EV-01).
- Other files in the repository with issue-5 artifacts were not used as sources. Only the library source was used.
- Next actions: resolve Q-01 first, then Q-02 and Q-03, and then run the FR-01-AC2 and FR-03-AC2 tests to check CLM-01.