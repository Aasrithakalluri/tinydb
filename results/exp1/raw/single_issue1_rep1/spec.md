# Requirements Specification: tinydb `!=` on missing fields
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue reporter): "`db.search(where('nickname') != 'bob')` only returns users that have a nickname other than bob. Users without a `nickname` are silently left out."
- S2 (issue reporter): "`db.search(~(where('nickname') == 'bob'))` returns users without a nickname too."
- S3 (issue reporter): "I'd expect `!=` to behave like the negation of `==`: a document that has no such field is 'not equal to bob', so it should be returned."
- S4 (issue reporter): example with docs `{'name':'a','nickname':'bob'}`, `{'name':'b','nickname':'al'}`, `{'name':'c'}`; `where('nickname') != 'bob'` returns only b; expected b and c.

## 2. Purpose and scope
- In scope: the result of `Query.__ne__` (`where(path) != value`) for documents where the path does not resolve. Source: S1, S3, S4.
- In scope: `!=` results for documents where the path resolves (must not change). Source: S4 (b and a are the stated cases).
- Out of scope: changes to `==`, `<`, `>`, `exists()`, or any other operator. Source: INFERRED from S3 (only `!=` is named).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "missing field" | S1, S3 | Path does not resolve (key absent, or a parent is not a dict) | AMBIGUOUS | Q-01 |
| "negation of ==" | S3 | `~(q == v)` semantics for every document | STATED | — |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | Developer who builds queries with `where()` / `Query()` and calls `Table.search` | INFERRED (S1, S3: the reporter writes such queries) |

## 5. Functional requirements

### FR-01: `!=` matches documents where the field is absent
Actor: ACT-01
Statement: WHEN a query `where(path) != value` is evaluated against a document where `path` does not resolve, the system SHALL return True for that document.
Source: STATED (S1, S3, S4)   |   Readiness: READY
Acceptance criteria:
- FR-01-AC1: document `{'name': 'c'}` with query `where('nickname') != 'bob'` → the query returns True, and `(~(where('nickname') == 'bob'))` also returns True for it.
- FR-01-AC2: document `{'nickname': 'bob'}` with query `where('nickname') != 'bob'` → the query returns False (present equal value stays excluded); document `{'nickname': None}` with the same query → returns True (present non-equal value, boundary of "present").
Notes: Behaviour is the reporter's stated expectation (S3). Test-level check only; the hash/cache key is unchanged.

### FR-02: `!=` on a path whose parent is not a dict
Actor: ACT-01
Statement: IF a parent segment of `path` resolves to a value that is not a dict (for example a string), THEN the system SHALL treat `path` as missing and return True for `!=`.
Source: ASSUMED (ASM-01)   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: document `{'profile': 'not-a-dict'}` with query `where('profile')['age'] != 30` → returns True; document `{'profile': {'age': 30}}` with the same query → returns False; document `{'name': 'x'}` → returns True.
Notes: Follows from ASM-01 (treat any unresolvable path the same as a missing field). Related to Q-01.

## 6. Non-functional requirements
None identified.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | Change must stay within `tinydb/` and `tests/`; no new dependencies | STATED (task brief) |
| CON-02 | Query hash must keep identifying what a query matches (ARCHITECTURE.md §3, rule 5) | STATED (ARCHITECTURE.md §3) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | Python standard library only | STATED (ARCHITECTURE.md §0: no runtime dependencies) | None identified |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Existing callers that rely on `!=` excluding documents without the field get different results | S1 vs S3 (behaviour change) | Silent change in search results for upgraders | Note in changelog; confirm with maintainers (Q-02) |
| RSK-02 | Nested-path semantics (FR-02) may differ from maintainers' intent | ASM-01, Q-01 | Wrong result for nested non-dict parents | Confirm Q-01 before relying on FR-02 |

## 10. External evidence log
None identified. No law, standard, named product or numeric external claim is used; no fetch call was needed (the tool was not used).

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED S1, S3, S4 | Q-02 (P3) | READY |
| FR-02 | ACT-01 | ASSUMED ASM-01 | Q-01 (P2) | NEEDS-CLARIFICATION |
| CON-01 | — | STATED | — | — |
| CON-02 | — | STATED | — | — |
| DEP-01 | — | STATED | — | — |

Open questions (for the register):
- Q-01 (P2): For a path whose parent is a non-dict value (e.g. `'not-a-dict'['age']`), should `!=` return True (treat as missing, ASM-01) or False?
- Q-02 (P3): Should the behaviour change be recorded in the changelog as a breaking change?

## 12. Change log
- 0.1: Initial spec from issue #1. No stakeholder available; questions left open.