# Requirements Specification: tinydb `is_empty()`
Version: 0.2 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue #30 title | "Add `is_empty()` to tables" |
| S2 | Issue #30 author | "Checking whether a table has any documents currently needs `len(db) == 0`, which reads badly in conditions." |
| S3 | Issue #30 author | "A method `db.is_empty()` returning `True` when the table has no documents and `False` otherwise would be nicer." |
| S4 | Issue #30 author | "It should also work on named tables: `db.table('users').is_empty()`." |

Stakeholders available to answer questions: none. All open questions are kept open (Section 9, document and continue).

## 2. Purpose and scope

**In scope**
- A boolean check that reports whether a table holds no documents (S2, S3).
- The check is available as a method on a named table, `db.table('users').is_empty()` (S4).
- The check is available as `db.is_empty()` on the database object (S3). Which table it refers to is ASSUMED (ASM-02, Q-01).

**Out of scope**
- Changing the existing behaviour of `len(db)`, `count()` and other existing methods. Source: ASSUMED (ASM-04). The issue does not ask for changes to them.
- Methods that take arguments, such as a query condition. Source: ASSUMED (ASM-01). The issue shows no arguments.
- Any implementation approach. Not requested (golden rule 6).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| table (named) | S4 | A table selected with `db.table(name)`. Clear. | Clear | None |
| default table | Repository, `tinydb/database.py` `__len__` (counts the default table) | The table used by `db` when no name is given. Meaning of `db.is_empty()` depends on this (options: default table, or no database-level method). | AMBIGUOUS | Q-01 |
| no documents | S3 | Document count equals 0. Measurable. | Clear | None |
| empty table that was never written to | Not stated | Options: returns True, or raises an error. | AMBIGUOUS | Q-02 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Python developer using tinydb | Writes code that checks whether a table or database has documents (S1, S2). | INFERRED (S1, S2): the issue author describes writing conditions with `len(db)`. |

## 5. Functional requirements

### FR-01: Table reports whether it has no documents
Actor: ACT-01
Statement: WHEN `is_empty()` is called on a table, the system SHALL return `True` if the table holds zero documents and `False` if it holds one or more.
Source: STATED (S3, S4) | Readiness: READY
Acceptance criteria:
- FR-01-AC1: a table with no documents → `is_empty()` returns `True`
- FR-01-AC2: a table with exactly one document → `is_empty()` returns `False`
- FR-01-AC3: a table whose documents have all been removed (boundary: zero after removal) → `is_empty()` returns `True`
- FR-01-AC4: a table with one document that is then removed and a new document inserted → `is_empty()` returns `False`
- FR-01-AC5: the return value of `is_empty()` on an empty table → the value is the `bool` object `True` (type is `bool`, not `0`, `None` or a truthy non-bool)

Notes: The issue names the method on tables in S4. Argument-free call is ASM-01. Related: ASM-01, ASM-03 (return type is bool, from S3).

### FR-02: Database object reports whether its default table has no documents
Actor: ACT-01
Statement: WHEN `is_empty()` is called on a database object, the system SHALL return `True` if the default table holds zero documents and `False` if it holds one or more.
Source: STATED (S3) for the method name and result; ASSUMED for the default-table meaning (ASM-02) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: a new database with two documents in its default table → `db.is_empty()` returns `False`
- FR-02-AC2: a new database with no documents in any table → `db.is_empty()` returns `True`
- FR-02-AC3: a database whose default table had documents, all removed → `db.is_empty()` returns `True`
- FR-02-AC4: a database with documents only in named table `users` and none in the default table (boundary: other tables ignored) → `db.is_empty()` returns `True`
- FR-02-AC5: a database with no documents → the return value of `db.is_empty()` is the `bool` object `True` (type is `bool`)

Notes: The database object already forwards unknown attribute access to the default table (`tinydb/database.py`, `__getattr__`). So `db.is_empty()` may already reach the default table through forwarding unless a database-level method is added. The issue does not say which is wanted, so this is open (Q-01, ASM-02). Risk RSK-01 applies. Blocked by Q-01 (P2).

### FR-03: Named table check is independent of other tables
Actor: ACT-01
Statement: WHEN `is_empty()` is called on a named table (for example `db.table('users')`), the system SHALL return the result for that named table only.
Source: STATED (S4) | Readiness: NEEDS-CLARIFICATION (Q-02)
Acceptance criteria:
- FR-03-AC1: table `users` with two documents → `db.table('users').is_empty()` returns `False`
- FR-03-AC2: table `users` whose documents have all been removed → `db.table('users').is_empty()` returns `True`
- FR-03-AC3: table `users` empty while table `posts` holds documents (boundary: other tables ignored) → `db.table('users').is_empty()` returns `True`
- FR-03-AC4: table name `users` that has never had a document written → TBD (Q-02)

Notes: The FR-03-AC4 criterion is unresolved. Option (a) returns `True`. Option (b) raises an error. Blocked by Q-02 (P2).

## 6. Non-functional requirements

### NFR-01: No regression in existing tests
Actor: System-wide
Statement: WHEN the repository test suite is run after the change, the system SHALL report zero failing tests that passed before the change.
Metric: count of previously passing tests that fail | Threshold: 0 | Condition: full run of the existing `tests/` suite on the same environment before and after the change.
Source: INFERRED (the issue asks for an addition, so existing behaviour must stay intact; no stakeholder stated this) | Readiness: NEEDS-CLARIFICATION (Q-03)
Acceptance criteria:
- NFR-01-AC1: existing suite run with the change applied → zero previously passing tests fail
- NFR-01-AC2: existing suite run with a deliberately broken `is_empty()` (returns the wrong value) → at least one test fails (boundary: the suite detects the defect)

Notes: The threshold `0` is an absolute, flagged as such (V7). It is a gate, not a claim of perfection. Blocked by Q-03 (P3) until the team confirms it is an acceptance gate.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | The issue states no time, budget, platform or technology constraint. | None |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| None identified | The issue names no external system, service or data. The library's own storage is part of the project, not an external dependency. | None | None |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | `db.is_empty()` may silently act on the default table through existing attribute forwarding, and a future change could make it refer to something else. | Repository `__getattr__` forwarding; Q-01, ASM-02 | Behaviour is unclear and may change without notice. | Resolve Q-01 and cover FR-02-AC1 to AC4 with tests. |
| RSK-02 | Behaviour for a table never written to is undefined. | S4 does not define it; Q-02 | Inconsistent results between versions or callers. | Resolve Q-02 before implementation. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None identified | No external fact (law, standard, product capability) is used by this specification. The issue names no external product. No fetch call was made. | None | None | None | None | None | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| ACT-01 | ACT-01 | INFERRED (S1, S2) | None | Not applicable |
| FR-01 | ACT-01 | STATED (S3, S4) | ASM-01, ASM-03 | READY |
| FR-02 | ACT-01 | STATED (S3); ASM-02 | Q-01, ASM-02, RSK-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | STATED (S4) | Q-02, RSK-02 | NEEDS-CLARIFICATION |
| NFR-01 | System-wide | INFERRED | Q-03 | NEEDS-CLARIFICATION |
| Q-01 (P2) | | | Blocks FR-02 | OPEN |
| Q-02 (P2) | | | Blocks FR-03-AC4 | OPEN |
| Q-03 (P3) | | | Blocks NFR-01 | OPEN |
| ASM-01 | | | FR-01 | Unconfirmed |
| ASM-02 | | | FR-02 | Unconfirmed |
| ASM-03 | | | FR-01, FR-02 | Unconfirmed |
| ASM-04 | | | Scope (Section 2) | Unconfirmed |

Open question register:
- Q-01 (P2): For `db.is_empty()`, should the result describe the default table (matching `len(db)`), or should the method exist only on named tables? Options: (a) default table; (b) no database-level method. Blocks FR-02. Ask: issue author or maintainers.
- Q-02 (P2): For `db.table('name').is_empty()` where no document was ever written to that name, should the result be (a) `True`, or (b) an error? Blocks FR-03-AC4. Ask: issue author or maintainers.
- Q-03 (P3): Is "no regression in the existing test suite" an acceptance gate for this change? Blocks NFR-01. Ask: maintainers.

Assumptions register:
- ASM-01: `is_empty()` takes no arguments. Basis: S3 and S4 show no arguments. Affects FR-01, FR-02. Risk if wrong: API mismatch with the issue's intent.
- ASM-02: `db.is_empty()` refers to the default table, as `len(db)` does. Basis: S3 and the repository's `__len__`. Affects FR-02. Risk if wrong: the method reports the wrong table.
- ASM-03: The result is a `bool`. Basis: S3 ("returning `True` ... and `False`"). Affects FR-01, FR-02.
- ASM-04: Existing methods, including `len()` and `count()`, keep their behaviour. Basis: the issue asks only for an addition. Affects Section 2 and NFR-01. Risk if wrong: scope grows.

Conflicts: None identified.

Unverified claims: None identified.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | Earlier | Previous draft. Failed validation: FR-02-AC5 had no arrow (→). |
| 0.2 | 2026-11-22 | Rewrote FR-02 acceptance criteria so every criterion uses →. Replaced the unclear FR-02-AC5 with a bool-type check. Added the scope, glossary, assumption and register sections. Kept IDs. Q-01 to Q-03 remain open. |