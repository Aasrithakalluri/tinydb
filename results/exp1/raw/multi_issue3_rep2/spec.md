# Requirements Specification: tinydb Issue #3, `count()` without a condition
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| S# | Speaker | Sentence |
|---|---|---|
| S1 | Issue author | To show "N records" on my page I do `db.count(...)` and I always have to invent a condition that is always true. |
| S2 | Issue author | Code sample: `db.count(where('id').exists())` is "not even right if docs don't have 'id'". |
| S3 | Issue author | `db.count()` with no arguments just raises a `TypeError`. |
| S4 | Issue author | It'd be nice if `count()` with nothing passed returned the total number of documents in the table. |
| S5 | Issue author | `count(some_query)` should keep working as today. |

Repository observation (not an input sentence): `tinydb/table.py` lines 709–716 define `Table.count(self, cond)` with `cond` required and `return len(self.search(cond))`. `Table.__len__` (lines 725–730) returns `len(self._read_table())`. This is the current behaviour that S3 describes.

Stakeholders available to answer: none in this pipeline run. All open questions are kept open.

## 2. Purpose and scope

**In scope**
- Calling `count()` with no argument returns the number of documents in the table. Source: STATED (S4).
- Calling `count(cond)` keeps its current result. Source: STATED (S5).

**Out of scope**
- Changing `search`, `__len__` or any other method. Source: INFERRED (the issue asks only about `count`).
- Database-level `count()` on the `TinyDB` object: TBD (Q-02). Source: OPEN.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| `count()` with no argument | S4 | (a) Table method with `cond` optional; (b) sentinel value used to mean "no condition". | AMBIGUOUS | Q-01 |
| `count(None)` (explicit None) | Not in input | (a) same as no argument; (b) raises as today. | AMBIGUOUS | Q-01 |
| `db` | S1, S2, S3 | (a) a `Table` instance; (b) the `TinyDB` object, which forwards to its default table. | AMBIGUOUS | Q-02 |
| "records" | S1 | Same as "documents" in S4 (assumed). | AMBIGUOUS | Q-03 |
| "total number of documents in the table" | S4 | All stored documents, including documents without an `'id'` field. | STATED (wording), interpretation ASSUMED (ASM-01) | — |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Uses tinydb to count stored documents for display. | INFERRED (from S1: the author counts records to show on a page) |

## 5. Functional requirements

### FR-01: Count all documents when no condition is given
Actor: ACT-01
Statement: WHEN `count()` is called with no condition argument, the system SHALL return the number of documents currently stored in the table.
Source: STATED (S4) | Readiness: NEEDS-CLARIFICATION (Q-02, Q-03; ASM-01)
Acceptance criteria:
- FR-01-AC1: a table holds 3 documents, one of which has no `'id'` field → `count()` returns 3.
- FR-01-AC2: an empty table (no documents inserted) → `count()` returns 0.
- FR-01-AC3: a table had 2 documents inserted and then 1 removed → `count()` returns 1.
- FR-01-AC4: a table holds 1 document and `count(where('x') == 1)` is called on a document with `'x'` set to 2 → `count()` still returns 1, showing the no-argument form ignores any filter.

Notes: ASM-01 (the interpretation): "total" means all stored documents in the table, including documents without `'id'`, as S2 implies. Calling on the `TinyDB` object is not covered here (Q-02). Explicit `count(None)` is not covered (Q-01). Related: CNF none, CLM none, EV none.

### FR-02: Keep counting with a condition unchanged
Actor: ACT-01
Statement: WHEN `count(cond)` is called with a condition, the system SHALL return the same number that the number of results of `search(cond)` has today.
Source: STATED (S5) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: a table holds `{'a': 1}`, `{'a': 2}` and `{}` and `cond` is `where('a') == 1` → `count(cond)` returns 1.
- FR-02-AC2: the same table and `cond` is `where('a') == 9` (matches nothing) → `count(cond)` returns 0.
- FR-02-AC3: the same table and `cond` is `where('a').exists()` → `count(cond)` returns 2, because the document without `'a'` is not matched.

Notes: The result must equal `len(table.search(cond))` for each case. The behaviour is unchanged from `tinydb/table.py` lines 709–716.

## 6. Non-functional requirements

None identified. The issue states no performance, availability or other quality measure.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | — | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| None identified | — | — | — |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | The meaning of explicit `count(None)` is undecided. Making it return the total changes behaviour that currently raises. | Q-01 | Callers relying on the error may change behaviour. Tests written for FR-01 could lock in an unapproved choice. | Ask the maintainer to choose between (a) treating `None` like no argument, or (b) keeping `None` as an error, before FR-01 tests are finalised. |
| RSK-02 | It is unclear whether `db.count()` on the `TinyDB` object must work, or only `Table.count()`. | Q-02 | If the maintainer expects the `TinyDB` form, FR-01 is incomplete. | Ask the maintainer. Confirm the `TinyDB` forwarding path before release. |
| RSK-03 | "Records" in S1 may not match "documents" in S4. | Q-03 | Low. The count could differ if the author means a different collection. | Confirm with the author. |

Escalation: Q-01 and Q-02 need a maintainer decision (no stakeholder present in this run).

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | No external fact is involved. The issue concerns tinydb's own API, and the repository was read only. | — | — | — | — | — | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S4) | Q-01, Q-02, Q-03, ASM-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S5) | none open | READY |
| ACT-01 | — | INFERRED (S1) | Q-03 | — |

Open questions:
- Q-01 (P1): Should explicit `count(None)` (a) return the total like `count()`, or (b) keep raising? Blocks FR-01 (tests and signature).
- Q-02 (P2): Must `db.count()` work on the `TinyDB` object (which forwards to its default table), or is `Table.count()` enough? Blocks FR-01 scope.
- Q-03 (P3): Does "records" in S1 mean documents in the default table? Blocks nothing directly.

Assumptions:
- ASM-01 (ASSUMED): "total number of documents in the table" means every stored document, including documents without `'id'`, and this is the count returned by `len(table)`. If wrong, FR-01 changes.

Conflicts: none identified.
Unverified claims: none.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial draft from Issue #3. FR-01 needs clarification (Q-01, Q-02, Q-03; ASM-01). FR-02 is READY. |