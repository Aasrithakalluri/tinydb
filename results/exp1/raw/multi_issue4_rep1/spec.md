# Requirements Specification: tinydb `multiply` update operation
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

Source: GitHub issue #4 in Aasrithakalluri/tinydb. Speaker: issue author (reporter, role not stated).

- S1 (title): "Add a `multiply` update operation"
- S2: "There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number."
- S3: "I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time."
- S4: "Would be great to have:" followed by the example `from tinydb.operations import multiply` and `db.update(multiply('price', 1.1), where('category') == 'books')`
- S5: "Same style as the other operations (takes the field name and the factor)."

Stakeholder availability: none present. No answers received. All open questions remain open.

## 2. Purpose and scope

- **In scope:** a `multiply(field, factor)` update operation in `tinydb.operations`, usable as the first argument of `db.update(...)` together with a query, which multiplies the named field of each matching document by `factor`. Source: STATED (S1, S4, S5).
- **Out of scope:** changes to existing operations (`add`, `subtract`, `increment`, `decrement`, `delete`, `set`), and other arithmetic such as division or percentage operations. Source: ASSUMED (ASM-04). The issue does not ask for them.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| scale a number | S2 | Multiply by a factor (the title and example confirm multiplication). Division is not requested. | Resolved by S1 and S4 | None |
| factor | S5 | Numeric multiplier passed as the second argument. Assumed to be `int` or `float`, matching the `Union[int, float]` type of `subtract`. | ASSUMED (ASM-03) | Q-03 |
| missing field | Derived from S4 | Matching document has no key with the field name. Options: raise `KeyError` (as siblings do), skip silently, or skip and report. | AMBIGUOUS | Q-01 |
| non-numeric field value | Derived from S4 | Matching document holds a value such as a string. Options: raise `TypeError`, skip, or accept Python semantics (an `int` factor repeats a string). | AMBIGUOUS | Q-02 |
| price change | S3 | Example only: a multiplication of a numeric field. Not a separate feature. | Example, not a requirement | None |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user (developer) | Applies a bulk numeric change to documents with `db.update` and a query. | STATED (S3, S4) |

## 5. Functional requirements

### FR-01: Multiply a numeric field in matching documents
Actor: ACT-01
Statement: WHEN `db.update(multiply(field, factor), query)` is called and a document matches the query and holds a numeric value in `field`, the system SHALL replace that value with the value multiplied by `factor`.
Source: STATED (S2, S3, S4) | Readiness: READY
Acceptance criteria:
- FR-01-AC1: Documents `{'price': 10, 'category': 'books'}` and `{'price': 5, 'category': 'toys'}` stored, then `db.update(multiply('price', 1.1), where('category') == 'books')` → the books document has `price` equal to 11.0 (compared with `pytest.approx`) and the toys document keeps `price` equal to 5.
- FR-01-AC2: Document `{'price': 10}` matched and `multiply('price', 1)` applied → `price` remains 10 (boundary: identity factor).
- FR-01-AC3: Document `{'price': 10}` matched and `multiply('price', 0)` applied → `price` equals 0 (boundary: zero factor).
- FR-01-AC4: Document `{'price': 10}` matched and `multiply('price', -2)` applied → `price` equals -20 (boundary: negative factor).
- FR-01-AC5: No stored document matches the query and `multiply('price', 2)` is applied through `db.update` → no document changes and no exception is raised (failure-free no-match case).
Notes: Basis is the title and example in S1 and S4. Float rounding is recorded as RSK-01 and Q-04 (P3, not blocking). Tests should compare float results with a tolerance. Related: CON-01, ASM-03.

### FR-02: Missing field on a matching document
Actor: ACT-01
Statement: IF a document matches the query and does not contain the field, THEN the system SHALL raise `KeyError`.
Source: ASSUMED (ASM-01) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-02-AC1: Document `{'category': 'books'}` stored (no `price` key), then `db.update(multiply('price', 1.1), where('category') == 'books')` → `KeyError` is raised.
- FR-02-AC2: Document `{'category': 'toys'}` without `price` stored and not matched by the query `where('category') == 'books'`, with `multiply('price', 1.1)` applied → the update completes with no exception and the toys document is unchanged (boundary: unmatched document without the field).
Notes: ASM-01 follows the behaviour of `add`, `subtract`, `increment` and `decrement` in `tinydb/operations.py`, which read `doc[field]` directly and so raise `KeyError`. The issue does not state this case. If Q-01 is answered with "skip", this requirement becomes SUPERSEDED. Whether documents changed before the exception stay changed is not verified here (see RSK-03).

### FR-03: Non-numeric field value on a matching document
Actor: ACT-01
Statement: IF a document matches the query and its value in the field is not a number, THEN the system SHALL raise `TypeError` and SHALL NOT change the stored value.
Source: ASSUMED (ASM-02) | Readiness: NEEDS-CLARIFICATION (Q-02)
Acceptance criteria:
- FR-03-AC1: Document `{'price': 'abc'}` matched and `multiply('price', 2)` applied (integer factor) → `TypeError` is raised and the stored `price` remains `'abc'` (boundary: integer factor, which would otherwise repeat the string).
- FR-03-AC2: Document `{'price': 'abc'}` matched and `multiply('price', 1.1)` applied (float factor) → `TypeError` is raised and the stored `price` remains `'abc'`.
Notes: Without a check, Python's `*` repeats a string for an integer factor (`'abc' * 2` gives `'abcabc'`), which would corrupt data silently (RSK-02). ASM-02 is the assumed behaviour, not a stated one. Q-02 must be answered before this requirement can be READY.

## 6. Non-functional requirements

None identified. No measurable quality (performance, scale, availability) was stated in the input. Rounding precision is recorded under Q-04 and RSK-01.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The operation SHALL follow the style of the existing operations: it takes the field name and the factor and returns a transform usable as the first argument of `db.update`. | STATED (S5, S4) |

## 8. Dependencies

None identified. The operation depends only on the existing `db.update` and query behaviour in this repository.

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Binary floating-point rounding makes results inexact (for example, 10 × 1.1 is not exactly 11). | S3 (price change with a decimal factor); Q-04 | Prices may differ from the decimal value users expect, and exact equality tests fail. | Document the behaviour; use tolerance in tests; decide with Q-04. |
| RSK-02 | An integer factor applied to a string field repeats the string silently. | Q-02, ASM-02 | Silent data corruption in stored documents. | Answer Q-02; implement FR-03 checks. |
| RSK-03 | If `KeyError` or `TypeError` is raised partway through an update, earlier matching documents may already be changed. | ASM-01, FR-02, FR-03 | Partial update that is hard to detect. Not verified in this spec. | Read the update path in `tinydb/table.py` before implementation and confirm the behaviour; decide whether failure should be atomic. |

## 10. External evidence log

None. No external fact (law, standard, named product or service, or numeric claim about the outside world) is involved. No fetch call was made.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | None | None | None | None | None | None | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S2, S3, S4) | Q-04 (P3, non-blocking), RSK-01 | READY |
| FR-02 | ACT-01 | ASSUMED (ASM-01) | Q-01 (P2) | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASSUMED (ASM-02) | Q-02 (P2), RSK-02 | NEEDS-CLARIFICATION |
| ACT-01 | n/a | STATED (S3, S4) | FR-01, FR-02, FR-03 | n/a |
| CON-01 | n/a | STATED (S5, S4) | FR-01 | n/a |
| ASM-01 to ASM-04 | n/a | ASSUMED | Q-01, Q-02, Q-03 | Unconfirmed |

## 12. Change log

- 0.1 (2026-11-22): Initial draft from issue #4. No stakeholder answers. No external evidence used. Repository experiment scripts that mention this issue were not used as a requirements source.

---

## Assumptions and open questions

**Open questions**

| Q | Question | Why it matters | Blocks | Priority | Ask whom | Status | Answer |
|---|---|---|---|---|---|---|---|
| Q-01 | For a matching document without the field, should `multiply` (a) raise `KeyError` as the sibling operations do (assumed), (b) skip that document silently, or (c) skip it and report it? | Determines FR-02 and data-consistency behaviour. | FR-02 | P2 | Issue author / maintainer | OPEN | |
| Q-02 | For a matching document whose field is not a number, should `multiply` (a) raise `TypeError` (assumed), (b) skip the document, or (c) follow Python semantics, where an integer factor repeats a string? | Option (c) corrupts data silently. | FR-03 | P2 | Issue author / maintainer | OPEN | |
| Q-03 | Should the factor accept only `int` and `float` (assumed), or also numeric strings or `Decimal`? | Sets the input contract of the factor. | Detail of FR-01 | P3 | Issue author / maintainer | OPEN | |
| Q-04 | Is float rounding acceptable (assumed), or should results be rounded to a fixed number of decimal places? | Affects exact prices and test comparisons. | None (RSK-01) | P3 | Issue author / maintainer | OPEN | |

**Assumptions**

| ASM | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-01 | A missing field on a matching document raises `KeyError`. | `add`, `subtract`, `increment` and `decrement` in `tinydb/operations.py` access `doc[field]` directly. | FR-02 | Different exception or silent skip; tests change. | Unconfirmed |
| ASM-02 | A non-numeric field value raises `TypeError` and is not changed. | Protects against silent string repetition (RSK-02). | FR-03 | Data corruption if the other behaviour is chosen. | Unconfirmed |
| ASM-03 | The factor is `int` or `float`. | Matches the `Union[int, float]` type of `subtract`. | FR-01 scope | Input contract changes. | Unconfirmed |
| ASM-04 | Only the new operation is added; existing operations do not change. | The issue asks only for `multiply`. | Scope | Extra work or regressions in other operations. | Unconfirmed |

**Conflicts:** None identified.

**Unverified claims:** None identified.

**Escalations to a human**

| Item | Reason | Needed from |
|---|---|---|
| Q-01, Q-02 | Behaviour for missing and non-numeric fields is not stated, and the choices affect data integrity. | Issue author or tinydb maintainer |

---

## Validation summary

Overall readiness: PARTIALLY READY (FR-01 is READY; FR-02 and FR-03 depend on open P2 questions and are ASSUMED).

**Counts:** Requirements: 3 FR (1 READY, 2 NEEDS-CLARIFICATION, 0 BLOCKED), 0 NFR. Questions: 0 P1, 2 P2, 2 P3. Assumptions: 4. Conflicts: 0. Claims: 0.

**Checks:**
- V1 (every S# traced): PASS. S1 to S5 map to FR-01, CON-01 and ACT-01.
- V2 (gap dimensions covered): PASS. Missing data cases are covered by Q-01 and Q-02. Other dimensions (NFR, deployment, security, out of scope) are recorded as None identified or as ASM-04.
- V3 (all sections present): PASS for this file. Other files are not produced in this stage.
- V4 (no contradictions): PASS. No conflicts found.
- V5 (unique IDs, valid labels): PASS.
- V6 (traceability): PASS. Every requirement has an actor, a source label and a source.
- V7 (feasibility): PASS. No absolutes or incompatible combinations found. RSK-03 records the unverified atomicity question.
- V8 (testability): PASS for FR-01 (five criteria, including boundary and no-match cases). FR-02 and FR-03 each have two criteria with a failure or boundary case. NFR: none.
- V9 (honesty of values): PASS. Values come from S4 (1.1, 'price', 'books') or from the test examples in the criteria. No other numbers are used.
- V10 (no inferred item marked READY): PASS. Only FR-01 is READY and it is STATED.

**Readiness rule:** FR-01 is READY. FR-02 is ASSUMED and linked to open Q-01. FR-03 is ASSUMED and linked to open Q-02.

**Evidence boundaries:**
- Stated: S1 to S5 (issue text).
- External: none.
- Needs confirmation: ASM-01 to ASM-04, Q-01 to Q-04, and the FR-02 and FR-03 behaviour.

**Tool usage:** Read-only inspection of `tinydb/operations.py` and a repository search. No external fetch was made because the issue involves no law, standard, named product or external numeric claim.

**Limitations of this specification:**
- The update path in `tinydb/table.py` was not read in full, so the failure behaviour in RSK-03 is unverified.
- The repository contains experiment scripts that refer to this issue number and propose different behaviour for missing fields. They were not used as a source of requirements because they are repository content, not stakeholder input. They should be reviewed by a maintainer.
- No stakeholder answered. All decisions in FR-02 and FR-03 are assumptions.

**Next actions:**
1. Q-01: choose the missing-field behaviour (raise `KeyError` or skip).
2. Q-02: choose the non-numeric behaviour (raise `TypeError` or skip).
3. Q-04: confirm that float rounding is acceptable.
4. Read the update path (`tinydb/table.py`) to verify RSK-03.