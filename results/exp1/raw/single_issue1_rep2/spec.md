# Requirements Specification: tinydb `!=` on documents without the field
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue author): "`!=` skips documents that don't have the field, but `~(... == ...)` doesn't"
- S2 (issue author): "I have a table of users where some records have no `nickname` at all."
- S3 (issue author): "I'd expect `!=` to behave like the negation of `==`: a document that has no such field is 'not equal to bob', so it should be returned."
- S4 (issue author): Example data `{'name':'a','nickname':'bob'}`, `{'name':'b','nickname':'al'}`, `{'name':'c'}`; `db.search(where('nickname') != 'bob')` returns only b; expected b and c.
- S5 (issue author): "Same logical question, two different answers." No requirement beyond S3 (restates it).

## 2. Purpose and scope
- In scope: the `!=` query operator in `tinydb/queries.py` (STATED, S1, S3, S4). Its result for documents lacking the queried field (STATED, S3, S4). Consistency with `~(== ...)` (INFERRED, S3). Query cache correctness for the changed operator (INFERRED, ADR-3).
- Out of scope: changing `==`, `<`, `>` or other operators (INFERRED, S1 names only `!=`). Storage, middleware and database changes (INFERRED, scope of the issue).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "missing field" | S2, S3 | The path cannot be resolved in the document (key absent, or a parent is not a mapping). | Defined in this spec | None |
| "negation of ==" | S3 | `~(q == v)` as implemented by `QueryInstance.__invert__`. | Defined in this spec | None |
| "equal" for values that are element-wise (e.g. numpy arrays) | none | Unknown whether `!=` must match `not ==` for such types. | AMBIGUOUS | Q-02 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | Developer who queries a TinyDB table with `where(...)` queries. | STATED (S2) |

## 5. Functional requirements

### FR-01: Inequality matches documents that lack the field
Actor: ACT-01
Statement: WHEN a query `where(f) != v` is evaluated against a document, the system SHALL return True if the document has no resolvable field f or its value differs from v, and False otherwise.
Source: STATED (S1, S3, S4) | Readiness: READY
Acceptance criteria:
- FR-01-AC1: document `{'name': 'a'}` (no `nickname`) and query `where('nickname') != 'bob'` → result is True
- FR-01-AC2: document `{'a': 5}` and query `where('a')['b'] != 1` (path cannot be resolved because `a` is not a mapping) → result is True
- FR-01-AC3: document `{'name': 'a', 'nickname': 'bob'}` and query `where('nickname') != 'bob'` → result is False
- FR-01-AC4: table holding `{'name':'a','nickname':'bob'}`, `{'name':'b','nickname':'al'}`, `{'name':'c'}` and `db.search(where('nickname') != 'bob')` → returned names are exactly b and c
Notes: S4 gives the expected output. The nested-path case is a failure-path boundary of the same rule.

### FR-02: Inequality is the negation of equality, including in the query cache
Actor: ACT-01
Statement: WHEN a query `where(f) != v` is evaluated, the system SHALL return the same truth value as `~(where(f) == v)` for every document, and SHALL NOT reuse cached results of `where(f) == v` for it.
Source: INFERRED (S3; ADR-3 and constraint 5 in ARCHITECTURE.md) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: document `{'name': 'c'}` and both `where('nickname') != 'bob'` and `~(where('nickname') == 'bob')` → both results are True
- FR-02-AC2: table with `{'name':'a','nickname':'bob'}` and `{'name':'c'}`, where `db.search(where('nickname') == 'bob')` runs first → subsequent `db.search(where('nickname') != 'bob')` returns only `c`, not the cached `a`
Notes: Q-01 asks whether the cache-separation requirement is confirmed. Related: ASM-01.

## 6. Non-functional requirements
None identified.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | Layering: `queries.py` imports only `utils` (ARCHITECTURE.md section 3, constraint 4). | STATED (ARCHITECTURE.md) |
| CON-02 | A query's hash must identify exactly what it matches (ARCHITECTURE.md section 3, constraint 5). | STATED (ARCHITECTURE.md) |

## 8. Dependencies
None identified.

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Users who relied on `!=` excluding documents without the field see different results. | S1, S3 (behaviour change) | Silent change in search results | Call out the change in release notes (maintainer). |
| RSK-02 | For element-wise value types, `!=` and `not ==` may differ. | Q-02, ASM-01 | Unexpected results for those types | Confirm scope (Q-02). |

## 10. External evidence log
None: no law, standard, named product or numeric claim about the outside world is involved. No fetch call was made.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S3, S4) | None open | READY |
| FR-02 | ACT-01 | INFERRED (S3, ARCHITECTURE ADR-3) | Q-01 | NEEDS-CLARIFICATION |
| ACT-01 | n/a | STATED (S2) | None | READY |
| CON-01, CON-02 | n/a | STATED (ARCHITECTURE.md) | None | READY |

## 12. Change log
- 0.1 (2026-11-22): Initial specification from issue #1.

Open questions and assumptions are in `assumptions-open-questions.md`:
- Q-01 (P3): Is the cache-separation requirement in FR-02 confirmed? Blocks FR-02.
- Q-02 (P3): For element-wise types, should `!=` match `not ==` exactly? Blocks scope of RSK-02.
- ASM-01 (ASSUMED): Ordinary scalar, string, list and dict values are the only types in scope; for them `!=` equals `not ==`.