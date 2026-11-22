# Requirements Specification: `!=` on documents that lack the queried field (tinydb Issue #1)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Speaker for all items: issue author (a single reporter; not confirmed as a maintainer). No stakeholder was available to answer questions.

| S# | Sentence |
|---|---|
| S1 | I have a table of users where some records have no `nickname` at all. |
| S2 | I wanted everyone whose nickname is not "bob": `db.search(where('nickname') != 'bob')`. |
| S3 | This only returns the users that have a nickname other than bob. |
| S4 | Users without a nickname are silently left out. |
| S5 | With `~`: `db.search(~(where('nickname') == 'bob'))`. |
| S6 | I get the users without a nickname too. |
| S7 | Same logical question, two different answers, which cost me an afternoon because I assumed they were equivalent. |
| S8 | I expect `!=` to behave like the negation of `==`: a document that has no such field is "not equal to bob", so the reporter expects it to be returned. |
| S9 | Example: insert `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}`, `{'name': 'c'}`. |
| S10 | `db.search(where('nickname') != 'bob')` returns only b; the reporter expects b and c. |

## 2. Purpose and scope

**In scope**
- Behaviour of `!=` (`Query.__ne__`) when the document does not contain the queried field. Source: S8, S10.
- Equivalence of `where(f) != v` with `~(where(f) == v)` for documents lacking `f`. Source: S7, S8.

**Out of scope**
- Other comparison operators (`<`, `>`, `<=`, `>=`, `search`, `matches`, `one_of`). Source: ASM-01 (not raised in input).
- Storage backends, indexing, performance and query caching. Source: not raised in input (no requirement).

**Assumptions**
- ASM-01: Only `!=` changes. Other operators keep their current behaviour. Basis: the issue concerns `!=` only. Risk if wrong: scope grows to all operators. Status: Unconfirmed.
- ASM-02: A nested path whose earlier segment is missing or not a mapping counts as "missing field" (same as a top-level missing key). Basis: current code already catches `KeyError` and `TypeError` on path resolution. Risk if wrong: FR-03 changes. Status: Unconfirmed.
- ASM-03: "No such field" means the key is absent. A key present with value `None` is a present field. Basis: S1 says "no nickname at all"; the reporter's example does not use `None`. Risk if wrong: FR-01 and FR-02 change. Status: Unconfirmed.

### 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "not equal" (`!=`) | S8 | Reporter: negation of `==`. Option (a): change `!=` only so missing fields match. Option (b): keep `!=` and document the difference. | AMBIGUOUS | Q-01 |
| "has no such field" with compared value `None` | S1, ASM-03 | Option (a): a missing field is not equal to `None` (negation of `==`). Option (b): a missing field is excluded. | AMBIGUOUS | Q-02 |
| "nested path" with missing or non-mapping intermediate | ASM-02 | Option (a): treat as missing (returns True). Option (b): raise an error. | AMBIGUOUS | Q-03 |

### 3.1 Open questions

| Q | Priority | Question | Blocks | Ask whom |
|---|---|---|---|---|
| Q-01 | P1 | Should `where(f) != v` return True for documents lacking `f` (option a, as the issue asks), which changes current results for callers who rely on excluding them, or should the behaviour stay and be documented (option b)? | FR-01, FR-02, RSK-01 | Repository maintainers (not identified in input) |
| Q-02 | P2 | For `where(f) != None`, should a document lacking `f` match (negation of `==`, option a) or be excluded (option b)? | FR-01 (None case) | Repository maintainers |
| Q-03 | P2 | For a nested path with a missing or non-mapping intermediate (ASM-02), should `!=` return True (a) or raise an error (b)? | FR-03 | Repository maintainers |
| Q-04 | P3 | Should `<`, `>`, `<=`, `>=` also be reviewed for missing fields, or stay out of scope (ASM-01)? | ASM-01 | Repository maintainers |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | A developer who queries a tinydb table with the Python API (`where(...)`, `~`, `!=`, `db.search`). | STATED (S1, S2) |

## 5. Functional requirements

### FR-01: `!=` returns documents that lack the queried field
Actor: ACT-01
Statement: WHEN a query `where(<field>) != <value>` is evaluated against a document that does not contain `<field>`, the system SHALL return True for that document.
Source: STATED (S8, S10) | Readiness: NEEDS-CLARIFICATION (Q-01, Q-02)
Acceptance criteria:
- FR-01-AC1: query `where('nickname') != 'bob'` evaluated on `{'name': 'c'}` → returns True.
- FR-01-AC2: query `where('nickname') != 'bob'` evaluated on `{}` (boundary: empty document) → returns True.
- FR-01-AC3: after inserting `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}` and `{'name': 'c'}`, `db.search(where('nickname') != 'bob')` → returns the documents named 'b' and 'c' and not 'a' (order not checked).
- FR-01-AC4: for each of the three documents in FR-01-AC3, `(where('nickname') != 'bob')(doc)` equals `(~(where('nickname') == 'bob'))(doc)` → the two results are equal for all three documents.
Notes: The reporter's expectation is S8. Repository reading (not an EV entry): `Query.__ne__` uses `_generate_test`, which returns False when path resolution raises `KeyError` or `TypeError` (tinydb/queries.py lines 243–244, 267–278). `QueryInstance.__invert__` negates the `==` test, so it returns True for a missing field (lines 136–138). The existing `test_ne` (tests/test_queries.py lines 65–75) does not cover missing fields. Changing this is a behaviour change (Q-01, RSK-01).

### FR-02: `!=` still excludes documents whose field equals the compared value
Actor: ACT-01
Statement: WHILE a document contains the queried field, the system SHALL return False for `where(<field>) != <value>` when the field value equals `<value>`, and True when it does not.
Source: INFERRED (S8: `!=` is the negation of `==`; for present fields the current code already does this, see `test_ne`) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: document `{'nickname': 'bob'}` with query `where('nickname') != 'bob'` → returns False.
- FR-02-AC2: document `{'nickname': 'al'}` with query `where('nickname') != 'bob'` → returns True.
- FR-02-AC3: document `{'nickname': None}` with query `where('nickname') != 'bob'` (boundary: present field with `None` value, ASM-03) → returns True.
- FR-02-AC4: document `{'nickname': ['bob']}` with query `where('nickname') != ['bob']` (boundary: list value) → returns False.
Notes: Regression guard. Its wording depends on Q-01 only in that the outcome for missing fields may not change; FR-02 is independent of Q-02.

### FR-03: `!=` on a nested path treats a missing or non-mapping parent as a missing field
Actor: ACT-01
Statement: IF a path segment before the last one is absent from a document or is not a mapping, THEN the system SHALL return True for `where(<path>) != <value>` on that document.
Source: ASSUMED (ASM-02; extension of FR-01 to nested paths, not in input) | Readiness: NEEDS-CLARIFICATION (Q-03)
Acceptance criteria:
- FR-03-AC1: document `{'profile': {}}` with query `where('profile').nickname != 'bob'` → returns True.
- FR-03-AC2: document `{}` with query `where('profile').nickname != 'bob'` (boundary: parent key absent) → returns True.
- FR-03-AC3: document `{'profile': 5}` with query `where('profile').nickname != 'bob'` (failure case: parent is not a mapping) → returns True without raising an exception.
- FR-03-AC4: document `{'profile': {'nickname': 'bob'}}` with query `where('profile').nickname != 'bob'` → returns False.
Notes: Depends on Q-03. Current code already catches `TypeError` for this path (tinydb/queries.py lines 243–244).

## 6. Non-functional requirements

None identified. The input states no performance, availability or security requirement.

## 7. Constraints

None identified. The input states no deadline, budget, platform or mandated technology.

## 8. Dependencies

None identified. Query evaluation is in-process; the input names no external system.

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Changing `!=` alters result sets for existing callers who rely on excluding documents without the field. | Q-01; S4, S6 | Silent change in query results for current users. | Decide Q-01 first; record the decision in the change log and release notes. |
| RSK-02 | `!=` and `~(==)` may disagree for `None` or nested paths if Q-02 and Q-03 are decided inconsistently. | Q-02, Q-03, ASM-02, ASM-03 | The equivalence in FR-01-AC4 fails for some inputs. | Resolve Q-02 and Q-03 together with Q-01; add equivalence tests for each decided case. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | No external fact is involved. The input cites no law, standard, product capability or numeric claim about the outside world. No fetch call was made. | N/A | N/A | N/A | N/A | FR-01 to FR-03 | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S8, S10) | Q-01, Q-02, RSK-01, RSK-02 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | INFERRED (S8) | Q-01, RSK-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASSUMED (ASM-02) | Q-03, RSK-02 | NEEDS-CLARIFICATION |
| ACT-01 | n/a | STATED (S1, S2) | n/a | n/a |
| ASM-01 | n/a | Assumption | Q-04 | n/a |
| ASM-02 | n/a | Assumption | Q-03 | n/a |
| ASM-03 | n/a | Assumption | Q-02 | n/a |
| CNF | n/a | None identified | n/a | n/a |
| CLM | n/a | None identified | n/a | n/a |

## 12. Change log

- 0.1 (2026-11-22): Initial specification from Issue #1. No stakeholder answers. Overall readiness NOT READY: Q-01 (P1) is open and no requirement is READY.