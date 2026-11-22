# Requirements Specification: tinydb `is_empty()` (Issue #30)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue #30 title | "Add `is_empty()` to tables" |
| S2 | Issue #30 author (unnamed) | "Checking whether a table has any documents currently needs `len(db) == 0`, which reads badly in conditions." |
| S3 | Issue #30 author | "A method `db.is_empty()` returning `True` when the table has no documents and `False` otherwise would be nicer." |
| S4 | Issue #30 author | "It should also work on named tables: `db.table('users').is_empty()`." |

No stakeholder was available to answer questions. Open items are recorded and the specification continues.

## 2. Purpose and scope

**In scope**
- A method `is_empty()` that returns `True` when a table has zero documents and `False` otherwise (S3).
- The same method on named tables, for example `db.table('users').is_empty()` (S4).
- A database-level `db.is_empty()` (S3). Which table it describes is ASSUMED (ASM-02, Q-01).

**Out of scope**
- Changes to the existing behaviour of `len(db)` or `len(table)`. Not requested in S1–S4. Source: ASSUMED (ASM-03).
- Other query or count methods. Not requested in S1–S4. Source: ASSUMED (ASM-03).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| table has no documents | S3 | The table's document count is zero. | Clear | — |
| named table | S4 | A table obtained with `db.table(name)`. | Clear | — |
| `db` (as a table) | S3 | Option (a): the default table, the one `len(db)` counts. Option (b): no table-level meaning, so no database-level method is added. | AMBIGUOUS | Q-01 |
| never-written table | S4 (implied) | A named table with no documents ever written. Option (a): `is_empty()` returns `True`. Option (b): an error is raised. | AMBIGUOUS | Q-02 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Developer using the tinydb Python API | Code that calls `is_empty()` on a table or database object, for example in conditions (S2, S3, S4). | INFERRED (S2, S3, S4). Reasoning: the issue is about calling an API in code, so a caller exists. Needs confirmation. |

## 5. Functional requirements

### FR-01: `is_empty()` on a table object
Actor: ACT-01
Statement: WHEN `is_empty()` is called on a table object, the system SHALL return `True` if the table contains zero documents and `False` if it contains one or more documents.
Source: STATED (S3)   |   Readiness: READY
Acceptance criteria:
- FR-01-AC1: a table with no documents, created with `TinyDB(storage=MemoryStorage).table('items')` → `is_empty()` returns `True`
- FR-01-AC2: boundary: a table with exactly one document inserted → `is_empty()` returns `False`
- FR-01-AC3: boundary: a table whose only document was removed with `table.remove(doc_ids=[id])` → `is_empty()` returns `True`
- FR-01-AC4: a table with one document removed and a different document inserted → `is_empty()` returns `False`
- FR-01-AC5: a table with no documents → the returned value is the `bool` object `True` (type check: `type(result) is bool`)
Notes: S3 gives the `True` and `False` cases. No open P1 or P2 question is linked to this requirement.

### FR-02: `is_empty()` on the database object
Actor: ACT-01
Statement: WHEN `is_empty()` is called on a `TinyDB` object, the system SHALL return `True` if the default table contains zero documents and `False` if it contains one or more documents.
Source: ASSUMED (ASM-02); the method name is STATED (S3)   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: a database whose default table holds two documents → `db.is_empty()` returns `False`
- FR-02-AC2: a new database with no documents in any table → `db.is_empty()` returns `True`
- FR-02-AC3: boundary: the default table's only document is removed → `db.is_empty()` returns `True`
- FR-02-AC4: boundary: documents exist only in named table `users` and the default table is empty → `db.is_empty()` returns `True`
- FR-02-AC5: a new database with no documents → the returned value is the `bool` object `True`
Notes: The criteria follow ASSUMED option (a). In the current repository, `TinyDB.__getattr__` (tinydb/database.py) forwards unknown attributes to the default table, so `db.is_empty()` may resolve through forwarding once `Table.is_empty()` exists. See RSK-01. If Q-01 chooses option (b), this requirement is replaced.

### FR-03: Named table results are isolated from other tables
Actor: ACT-01
Statement: WHEN `is_empty()` is called on the object returned by `db.table(name)`, the system SHALL return the emptiness of the table named `name` only, without counting documents in any other table.
Source: STATED (S4)   |   Readiness: NEEDS-CLARIFICATION (Q-02)
Acceptance criteria:
- FR-03-AC1: table `users` with two documents → `db.table('users').is_empty()` returns `False`
- FR-03-AC2: table `users` whose documents were all removed → `db.table('users').is_empty()` returns `True`
- FR-03-AC3: boundary: table `users` is empty while table `posts` holds one document → `db.table('users').is_empty()` returns `True`
- FR-03-AC4: boundary: table `archive` has never had a document written → `db.table('archive').is_empty()` returns `True` (ASSUMED option (a) of Q-02; if option (b) is chosen, the expected result becomes an error raised by the call)
Notes: FR-03-AC4 is blocked by Q-02 (P2). The other criteria are not affected by Q-02.

## 6. Non-functional requirements

None identified. S1–S4 state no quality attribute, metric or threshold.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | S1–S4 state no time, budget, platform or technology constraint. | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| None identified | No external system, service or data source is needed. Existing in-repository table reads are internal to the library. | — | — |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | `db.is_empty()` may silently act on the default table through the existing attribute forwarding in `TinyDB.__getattr__`, and a later change could alter that meaning without notice. | Repository observation (tinydb/database.py); Q-01; ASM-02 | Behaviour is implicit and could change without a visible API change. | Resolve Q-01 and cover FR-02-AC1 to AC5 with automated tests. |
| RSK-02 | A named table that was never written to may return a result that callers do not expect. | S4; Q-02 | Conditions based on `is_empty()` may take the wrong branch. | Resolve Q-02 and cover FR-03-AC4 with an automated test. |

## 10. External evidence log

No external evidence was needed. The issue does not mention a law, standard, named product or external numeric claim, so no fetch call was made. All behaviour in this specification comes from the issue text (S1–S4) and the repository's current code.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None identified | — | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S3) | None | READY |
| FR-02 | ACT-01 | ASSUMED (ASM-02); S3 | Q-01, RSK-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | STATED (S4) | Q-02, RSK-02 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S2, S3, S4) | None | — |
| ASM-02 | — | ASSUMED | Q-01 | — |
| ASM-03 | — | ASSUMED | None | — |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from the Issue #30 text. No stakeholder answers. Q-01 and Q-02 are open. |