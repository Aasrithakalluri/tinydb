# Requirements Specification: tinydb: `multiply` update operation (Issue #4)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue author (unnamed) | "Add a `multiply` update operation" |
| S2 | Issue author | "There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number." |
| S3 | Issue author | "I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time." |
| S4 | Issue author | "Would be great to have: `from tinydb.operations import multiply` / `db.update(multiply('price', 1.1), where('category') == 'books')`" |
| S5 | Issue author | "Same style as the other operations (takes the field name and the factor)." |

Stakeholders available to answer: none. All open questions are kept open.

Repository check (read-only): `tinydb/operations.py` has `delete`, `add`, `subtract`, `set`, `increment`, `decrement`. It has no `multiply`. `add` and `subtract` apply `doc[field] op= n` directly, so a missing field raises `KeyError` and a non-numeric value raises `TypeError` (for example `'ten' - 1`).

## 2. Purpose and scope

**In scope**
- A new function `multiply(field, factor)` in `tinydb.operations` that returns an update transform for `db.update(...)`. Source: STATED (S1, S4, S5).
- Multiplying the value of one named field by one factor in each matched document. Source: STATED (S3, S4).

**Out of scope**
- Changes to `add`, `subtract`, `increment` or `decrement`. Source: ASSUMED (ASM-01), because the issue asks only for a new operation.
- Division, percentage or compound-scaling variants. Source: ASSUMED (ASM-01); see Q-05.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "scale a number" | S2 | (a) multiply the field by a factor; (b) multiply by a percentage; (c) a general scale that also divides. Working reading: (a), per S4 and S5. | AMBIGUOUS | Q-05 |
| "the factor" | S5 | A numeric multiplier (for example 1.1 means +10%). Whether 0 and negative factors are accepted is not stated. | AMBIGUOUS | Q-06 |
| "same style as the other operations" | S5 | (a) same call shape `op(field, value)`; (b) same error behaviour for missing or non-numeric fields as `add` and `subtract`. Working reading: (a) is STATED; (b) is ASSUMED. | AMBIGUOUS | Q-01, Q-02 |
| "everything" | S3 | The documents matched by the `where` clause, not the whole table. Read from S4. | AMBIGUOUS (resolved by S4) | None |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Developer using tinydb | Python developer who calls `db.update(multiply(...), where(...))` to change numeric field values. Inferred from S3 ("I need…", "write my own lambda"). | INFERRED (S3). Needs confirmation. |

## 5. Functional requirements

### FR-01: Multiply a numeric field in matched documents
Actor: ACT-01
Statement: WHEN `db.update(multiply(field, factor), <query>)` runs, the system SHALL multiply the numeric value of `field` by `factor` in every document matched by `<query>`, and SHALL leave the value of `field` in non-matched documents unchanged.
Source: STATED (S1, S4, S5)   |   Readiness: READY
Acceptance criteria:
- FR-01-AC1: table contains `{'category': 'books', 'price': 10}` and `{'category': 'toys', 'price': 10}`; `db.update(multiply('price', 1.1), where('category') == 'books')` runs → books document `price` equals 11.0 (compared with `pytest.approx`); toys document `price` stays 10.
- FR-01-AC2: document `{'price': 5}` (int) and `multiply('price', 2)` runs through `db.update` → stored `price` equals 10 with the same value.
- FR-01-AC3: document `{'price': 7}` and `multiply('price', 1)` runs → stored `price` equals 7 (boundary: identity factor).
- FR-01-AC4: the `where` query matches no document and `multiply('price', 1.1)` runs → the call returns without error and no stored value changes (boundary: empty match).
Notes: Floating-point rounding applies, for example 10 × 1.1 = 11.000000000000002, so tests SHALL compare with a tolerance. The return value of `db.update` is not specified here; it is treated as the existing tinydb behaviour (not in scope). Related: S4 usage example.

### FR-02: Missing field
Actor: ACT-01
Statement: IF the matched document has no key named `field`, THEN the system SHALL raise `KeyError` and SHALL leave that document unchanged.
Source: ASSUMED (ASM-02; based on the `subtract` and `add` behaviour in the repository, not on S-text)   |   Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: document `{'name': 'x'}` and `multiply('price', 1.1)` runs through `db.update` with a query that matches it → `KeyError` is raised and the document still equals `{'name': 'x'}`.
- FR-02-AC2: document `{'price': 0}` and `multiply('price', 1.1)` runs → no error is raised and `price` equals 0 (boundary: present field with zero value).
Notes: Alternatives are listed in Q-01 (skip silently, or treat as 0). If Q-01 answers differently, this FR is revised.

### FR-03: Non-numeric field value
Actor: ACT-01
Statement: IF the value of `field` in a matched document is not an `int` or `float`, THEN the system SHALL raise `TypeError` and SHALL leave that value unchanged.
Source: ASSUMED (ASM-03; based on the Python behaviour of `add`/`subtract` with non-numeric values in the repository)   |   Readiness: NEEDS-CLARIFICATION (Q-02, Q-03)
Acceptance criteria:
- FR-03-AC1: document `{'price': 'ten'}` and `multiply('price', 1.1)` runs → `TypeError` is raised and `price` still equals `'ten'`.
- FR-03-AC2: document `{'price': None}` and `multiply('price', 2)` runs → `TypeError` is raised and `price` still equals `None` (failure case: missing value).
Notes: For a string value, Python's `str * int` repeats the string without error. Whether `multiply('name', 2)` on a string should be rejected is open (Q-03). The acceptance criteria above cover only the `float` factor case, where Python raises `TypeError`.

## 6. Non-functional requirements

None identified. The issue states no performance, reliability, security or scale targets. If they are needed, they will be raised as new questions; no TBD values are invented here.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | The issue sets no deadline, budget, platform or mandated technology. | N/A |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | The existing `db.update(operation, query)` call accepts a transform function, as used in S4 and as documented in `tinydb/operations.py`. | STATED (S4) | If the update API changes, FR-01 to FR-03 cannot be tested through `db.update`. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Silent data change if a string field is multiplied by an int factor (Python repeats the string). | Q-03 | Corrupted values with no error. | Resolve Q-03 before implementation; add a test for the chosen behaviour. |
| RSK-02 | Callers may rely on a different missing-field behaviour (silent skip) than the one implemented. | Q-01, ASM-02 | Surprise `KeyError` in price-update scripts. | Resolve Q-01; document the chosen behaviour in the docstring. |
| RSK-03 | Float rounding makes exact-equality tests fail, and stored prices may drift after repeated updates. | S4 (factor 1.1) | Incorrect totals in price calculations. | Tests use tolerance; document that results are floats. |

## 10. External evidence log

No external evidence was needed. The issue names no law, regulation, standard, product or service, and makes no numeric claim about the outside world.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S4, S5) | None open (Q-06 and ASM-02 do not affect its criteria) | READY |
| FR-02 | ACT-01 | ASSUMED (ASM-02) | Q-01 (P2) | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASSUMED (ASM-03) | Q-02 (P2), Q-03 (P2) | NEEDS-CLARIFICATION |
| ACT-01 | N/A | INFERRED (S3) | Confirmation of actor | NEEDS-CLARIFICATION |
| DEP-01 | ACT-01 | STATED (S4) | None | READY (dependency) |
| ASM-01 | N/A | ASSUMED | Q-05 | Unconfirmed |

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | First draft from Issue #4. No stakeholder answers. Open questions Q-01 to Q-06 recorded. |

## Assumptions and open questions (register summary)

**Open questions**

| Q | Question | Why it matters | Blocks | Priority | Ask whom | Status |
|---|---|---|---|---|---|---|
| Q-01 | When a matched document has no `field`, should `multiply` (a) raise `KeyError` like `add`/`subtract`, (b) skip the document silently, or (c) treat the value as 0? | Decides FR-02 behaviour. | FR-02 | P2 | Issue author | OPEN |
| Q-02 | When the value is not `int` or `float` (for example `None`), should `multiply` raise `TypeError` (a), or do nothing (b)? | Decides FR-03 failure behaviour. | FR-03 | P2 | Issue author | OPEN |
| Q-03 | For a string value with an `int` factor, should `multiply` (a) reject the value with `TypeError`, or (b) allow Python's repetition? | Prevents silent corruption (RSK-01). | FR-03 | P2 | Issue author | OPEN |
| Q-05 | Is `multiply` the only new operation wanted, or also a divide or percentage variant? | Confirms ASM-01 and scope. | ASM-01 | P2 | Issue author | OPEN |
| Q-06 | Should factors 0 and negative values be accepted, or rejected with an error at call time? | Defines the factor domain (ASM-04). | None of the current FRs | P3 | Issue author | OPEN |

**Assumptions**

| ASM | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-01 | Only `multiply` is added. No change to other operations. | S1 names only `multiply`. | Scope | Extra work or missed variants. | Unconfirmed |
| ASM-02 | A missing field raises `KeyError` and leaves the document unchanged. | Same as `add` and `subtract` in the repository. | FR-02 | Different behaviour for users who expect a skip. | Unconfirmed |
| ASM-03 | A non-numeric value raises `TypeError` and is left unchanged. | Python behaviour of `None * n` and `'ten' * 1.1`. | FR-03 | Silent corruption if Q-03 chooses to allow strings. | Unconfirmed |
| ASM-04 | Factors that are `int` or `float` (including 0 and negative values) are accepted without error. | S5 ("takes the factor"); no restriction stated. | FR-01 (not in ACs) | Factor validation added later. | Unconfirmed |

**Conflicts:** None identified.

**Unverified claims:** None identified.

**Escalations to a human:** None required at this time. Q-01 and Q-02 should be answered by the issue author before implementation.

## Validation summary

Overall readiness: PARTIALLY READY (FR-01 is READY; FR-02 and FR-03 need answers to Q-01 to Q-03).

- Counts: READY requirements 1 (FR-01). NEEDS-CLARIFICATION 2 (FR-02, FR-03). BLOCKED 0. Open questions: 5 (P1: 0; P2: 4; P3: 1). Assumptions: 4. Conflicts: 0. Unverified claims: 0.
- Checks: V1 PASS (S1 to S5 traced). V2 PASS (gaps covered by Q-01 to Q-06 or "None identified"). V3 PASS. V4 PASS (no conflicts). V5 PASS (unique IDs). V6 PASS (every FR has an actor). V7 PASS (no absolutes or infeasible combinations). V8 PASS (FR-01 has four criteria with boundary and failure cases; FR-02 and FR-03 each have two). V9 PASS (ASSUMED items labelled). V10 PASS (no ASSUMED item marked READY).
- Evidence boundaries: STATED (S1 to S5, DEP-01); EXTERNAL none; needs confirmation: ACT-01, ASM-01 to ASM-04, FR-02, FR-03, Q-01 to Q-06.
- Tool usage: no external fetch was needed. One read-only repository check was done (`tinydb/operations.py`, plus a grep for existing `multiply` definitions).
- Limitations: no stakeholder was available; the spec is a draft from one issue. The missing-field and non-numeric behaviours are inferred from existing operations, not from the issue.
- Next actions: (1) Answer Q-01 (missing field). (2) Answer Q-02 and Q-03 (non-numeric values). (3) Confirm ASM-01 (scope) via Q-05. Then re-run validation in revision mode.