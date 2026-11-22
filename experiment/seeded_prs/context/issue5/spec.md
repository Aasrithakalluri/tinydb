# Requirements Specification: tinydb result ordering (issue #5)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Speaker for all sentences: GitHub issue #5 reporter (unnamed). No stakeholder is available to answer questions.

| S# | Sentence |
|---|---|
| S1 | "Results come back in a strange order" |
| S2 | "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right." |
| S3 | "I don't know exactly when it happens, but it seems related to how I created or changed the documents." |
| S4 | "It also looks different after I close and reopen the program." |
| S5 | "I'd like the order to be sensible and predictable, so my page doesn't jump around." |

Scope check: this is a software problem (the tinydb Python library). No out-of-scope requests were found.

Repository observations (code reading only, not external evidence):
- `tinydb/table.py:235-247`: `Table.all()` returns `list(iter(self))`.
- `tinydb/table.py:732-742`: `Table.__iter__` iterates `_read_table()` in its stored order.
- `tinydb/table.py:249-297`: `Table.search()` builds results by iterating `_read_table()` in stored order and caches the list.
- `tinydb/table.py:779-802`: `_read_table()` returns the stored table dict without sorting.
- `tinydb/storages.py:147`: `JSONStorage.write` calls `json.dumps(data, **self.kwargs)`. The default kwargs are OPEN (Q-04).
- `tests/test_storages.py:33`: a test constructs TinyDB with `sort_keys=True`, which shows that sorted-key output is a configuration in use.

## 2. Purpose and scope

**In scope (ASSUMED, ASM-01 to ASM-04):**
- Defining and enforcing a deterministic order for `Table.all()` and `Table.search()` results.
- Keeping that order stable across document updates, removals and a close/reopen cycle of the database file.

**Out of scope (ASSUMED, pending Q-06):**
- Sorting by a user-specified field or adding a new sort parameter.
- Changing the order of `Table.get(cond)` beyond what is stated in its existing docstring.

Source for all scope items: S5 (STATED for the goal "sensible and predictable order"). The exact order rule is ASSUMED (see ASM-01).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| sensible | S5 | (a) insertion order; (b) ascending document ID; (c) most recently modified last; (d) user-chosen sort key | AMBIGUOUS | Q-01 |
| predictable | S5 | Same input history gives the same order every time (interpretation adopted: deterministic across runs and reopen) | AMBIGUOUS | Q-01 |
| jump around | S5 | Documents change position after an update, removal or reopen (interpretation adopted) | AMBIGUOUS | Q-01 |
| doesn't look right | S2 | Unspecified expected order | AMBIGUOUS | Q-01 |
| changed (documents) | S3 | Update, upsert, removal, or re-insert; each may affect order differently | AMBIGUOUS | Q-02 |
| different after reopen | S4 | Order differs after the file is reloaded (cause not yet confirmed; see RSK-01) | OPEN | Q-04 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | A person who uses the tinydb Python API (`db.all()`, `db.search()`) to read documents in an ordered page. | INFERRED (S1, S2, S5: "my page"; reporter is a library user) |

## 5. Functional requirements

### FR-01: Stable order for all()
Actor: ACT-01
Statement: WHEN the application calls `Table.all()`, the system SHALL return all stored documents in insertion order (the order in which each document was first inserted), and SHALL keep the relative order of the remaining documents unchanged after an update or a removal.
Source: ASSUMED (ASM-01, ASM-02, ASM-03; basis S2, S3, S5) | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-02 P2)
Acceptance criteria:
- FR-01-AC1: a table has documents with IDs 1, 2, 3 inserted in that order, and document 1 is then updated with `update({'v': 9}, doc_ids=[1])` → `all()` returns documents with doc_id values [1, 2, 3] in that order.
- FR-01-AC2: a table has documents with IDs 1, 2, 3, and document 2 is removed with `remove(doc_ids=[2])` → `all()` returns doc_id values [1, 3].
- FR-01-AC3 (boundary): a table with 12 inserted documents → `all()` returns doc_id values [1, 2, ..., 12] in numeric order, not lexical order (1, 10, 11, 12, 2, ...).
- FR-01-AC4 (boundary): an empty table, or a table where every document has been removed → `all()` returns an empty list.
Notes: ASM-01 defines insertion order as the rule. Q-01 offers alternatives (ascending ID, last-modified order, user sort key). Q-02 decides whether an update moves a document to the end (changes FR-01-AC1). The statement that updates keep position is INFERRED from the dict-based storage model and must be confirmed by test. Related: RSK-01, RSK-02.

### FR-02: Same relative order for search()
Actor: ACT-01
Statement: WHEN the application calls `Table.search(cond)`, the system SHALL return the matching documents in the same relative order that `Table.all()` uses for the same table state, including when the result is served from the query cache.
Source: ASSUMED (ASM-04; basis S2: "`db.all()` and `db.search(...)`") | Readiness: NEEDS-CLARIFICATION (Q-01 P1)
Acceptance criteria:
- FR-02-AC1: a table has documents with IDs 1, 2, 3 and `search(where('k') == 'x')` matches documents 3 and 1 → `search` returns doc_id values [1, 3].
- FR-02-AC2: the same search is called twice with no change between calls, with an update to document 1 between them that keeps it matching → the second call returns the same order as the first call, and the order matches the relative order from `all()`.
- FR-02-AC3 (failure/boundary): a search with no matching documents → `search` returns an empty list.
Notes: Repository observation: `search()` caches results (`table.py:263-297`). The cache must not change order. Q-01 applies.

### FR-03: Order preserved across close and reopen
Actor: ACT-01
Statement: WHEN the application closes a database that uses the default JSON file storage and then reopens the same file, the system SHALL return `all()` and `search()` results in the same relative order as before the close.
Source: ASSUMED (ASM-04; basis S4: "after I close and reopen the program") | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-04 P2)
Acceptance criteria:
- FR-03-AC1 (boundary): a JSON-backed database with 12 documents is created with default storage options, closed, and reopened from the same path → `all()` returns doc_id values [1, 2, ..., 12] in the same order as before the close.
- FR-03-AC2: a JSON-backed database has documents inserted, one updated and one removed, then is closed and reopened → `all()` after reopen returns the same doc_id sequence as `all()` immediately before close.
- FR-03-AC3 (failure): a JSON-backed database is reopened after a close with an empty file or with no table → `all()` returns an empty list.
Notes: RSK-01 describes the likely cause: `JSONStorage.write` passes `self.kwargs` to `json.dumps`, and if `sort_keys=True` is set, the document ID keys are sorted as strings, which gives "1, 10, 11, 2, ...". Whether default kwargs sort keys is OPEN (Q-04). Whether this requirement applies to custom storages is OPEN (Q-03).

## 6. Non-functional requirements

None identified. The issue states no measurable quality requirement (no speed, size or availability target). A metric would need a stakeholder answer (TBD (Q-05), P3).

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | The issue names no deadline, budget, platform or technology constraint. | N/A |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | The on-disk JSON file written by `JSONStorage`, read back on reopen | INFERRED (S4: "close and reopen") | If the file is rewritten with a different key order by an external tool, order changes without any tinydb code change. Low likelihood; unassessed. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | JSON storage with `sort_keys=True` writes document ID keys in string order, so reopened results come back as 1, 10, 11, 2, ... | S4; `storages.py:147`; `tests/test_storages.py:33`; Q-04 | Order changes after reopen (the reported symptom). | Confirm default kwargs (Q-04). Add the FR-01-AC3 and FR-03-AC1 tests with default and `sort_keys=True` settings. |
| RSK-02 | Changing the order rule may break users who depend on the current order | Q-01 (order rule is not confirmed) | Behaviour change for existing callers. | Decide the rule with Q-01 and record it in the change log. Ask whether a migration note is needed (Q-07, P3). |
| RSK-03 | Ordering rule is unknown, so any implementation may not match the reporter's expectation | S1, S2, S5; Q-01 | Work done against the wrong rule. | Block implementation until Q-01 is answered. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | No external fact (law, standard, named product capability or numeric claim about the outside world) is needed for this issue. Repository code was read instead. | N/A | N/A | N/A | N/A | N/A | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| ACT-01 | N/A | INFERRED (S1, S2, S5) | Q-01 | NEEDS-CLARIFICATION |
| FR-01 | ACT-01 | ASSUMED (ASM-01 to ASM-03; S2, S3, S5) | Q-01 (P1), Q-02 (P2), RSK-01, RSK-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | ASSUMED (ASM-04; S2) | Q-01 (P1), RSK-03 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASSUMED (ASM-04; S4) | Q-01 (P1), Q-03 (P2), Q-04 (P2), RSK-01 | NEEDS-CLARIFICATION |
| DEP-01 | ACT-01 | INFERRED (S4) | Q-04 | NEEDS-CLARIFICATION |
| RSK-01 | N/A | S4; repository code | Q-04 | Open risk |
| RSK-02 | N/A | Q-01 | Q-07 | Open risk |
| RSK-03 | N/A | S1, S2, S5 | Q-01 | Open risk |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from issue #5. Order rule is ASSUMED (insertion order). Questions Q-01 to Q-07 are open. No stakeholder answers were available, and no external evidence was needed. |

### Open questions (summary)

- **Q-01 (P1), blocks FR-01, FR-02, FR-03.** What does "sensible and predictable" mean? Options: (a) insertion order (ASM-01, the adopted assumption); (b) ascending document ID; (c) most recently modified last; (d) a user-specified sort key. Ask: the issue reporter, or the tinydb maintainer who owns the ordering contract.
- **Q-02 (P2), blocks FR-01-AC1.** After an update, should the document keep its position (a), or move to the end (b)?
- **Q-03 (P2), blocks FR-03.** Should the order guarantee also apply to custom storage classes, or only to `JSONStorage` and `MemoryStorage`?
- **Q-04 (P2), blocks FR-03-AC1 and RSK-01.** With default `JSONStorage` options (no `sort_keys`), do document ID keys keep insertion order after reopen? Confirm by test, then decide whether to change the default.
- **Q-05 (P3).** Is there any measurable performance requirement for ordering (for example, a maximum time for `all()` on N documents)? If not, the NFR is closed as "none".
- **Q-06 (P3).** Is a user-specified sort parameter (for example, `all(sort_by=...)`) in scope? Assumed out of scope.
- **Q-07 (P3).** Should existing users who depend on the current order receive a migration note (RSK-02)?

### Escalations

- Q-01 needs a decision from the issue reporter or the maintainer before any implementation starts. No one was available to answer.