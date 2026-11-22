# Requirements Specification: tinydb `multiply` update operation (issue #4)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue #4 author | "There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number." |
| S2 | Issue #4 author | "I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time." |
| S3 | Issue #4 author | Requested usage: `db.update(multiply('price', 1.1), where('category') == 'books')` |
| S4 | Issue #4 author | "Same style as the other operations (takes the field name and the factor)." |

Repository check (read-only): `tinydb/operations.py` defines `delete`, `add`, `subtract`, `set`, `increment`, `decrement` and no `multiply`, which is consistent with S1. Existing operations return a transform callable that mutates the document. `tinydb/table.py` defines `update(...)`, which takes such a transform and a query.

Stakeholders: the issue author is the only known party. No one was available to answer questions in this run, so all questions remain open.

## 2. Purpose and scope

**In scope**
- A new public operation `multiply(field, factor)` in `tinydb.operations`, used as the first argument of `db.update(...)` (S1, S2, S3).
- Multiplying a numeric document field by a numeric factor (S2, S3).
- Matching the calling style of the existing operations: field name first, then the factor (S4).

**Out of scope**
- Operations other than `multiply` (S1 names only the existing ones).
- Changes to `db.update` or the query system.
- Exact decimal arithmetic. No stakeholder requested it. Recorded as RSK-01 and Q-08.

**Out of scope or open**
- Documentation updates to `docs/usage.rst` and the module docstring. Recorded as Q-07.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| multiply | S3 | Multiply the field's stored value by the factor and store the result in the same field. | STATED | — |
| scale (a number) | S1 | Options: (a) multiply in place (chosen as working meaning, ASM-01); (b) return a new document. | AMBIGUOUS | Q-04 |
| factor | S2, S4 | Options: int or float only (ASM-02); also str or bool. | AMBIGUOUS | Q-03, Q-05, Q-06 |
| same style | S4 | Options: field first, factor second, transform callable that mutates the document and returns None (chosen, ASM-01). | AMBIGUOUS | Q-02 |
| price change | S2 | The example field name is `price` and the example factor is `1.1`. These are examples, not a fixed API. | STATED | — |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer using the TinyDB Python API | Calls `db.update(multiply(...), query)` to change numeric fields in bulk. | INFERRED (S2: the author applies price changes through the API; S3 shows the call form) |

## 5. Functional requirements

### FR-01: Multiply a numeric field by a factor
Actor: ACT-01
Statement: WHEN the transform returned by `multiply(field, factor)` is applied to a document whose `field` holds a number, the system SHALL replace that value with the value multiplied by `factor` and return None.
Source: STATED (S1, S3, S4) for the operation and its arguments; ASSUMED (ASM-01) for in-place mutation and return value | Readiness: NEEDS-CLARIFICATION (Q-04, Q-08; ASM-01, ASM-02)
Acceptance criteria:
- FR-01-AC1: document `{'price': 10}` with `multiply('price', 1.1)` applied → `doc['price']` equals 11.0 within 1e-9 and the transform returns None.
- FR-01-AC2: document `{'n': 7}` with `multiply('n', 2)` applied → `doc['n']` equals 14 and is an int (int × int stays int).
- FR-01-AC3: document `{'price': 10}` with `multiply('price', 0)` applied → `doc['price']` equals 0 (boundary: zero factor, see Q-04).
- FR-01-AC4: document `{'price': 10}` with `multiply('price', -1)` applied → `doc['price']` equals -10 (boundary: negative factor, see Q-04).
- FR-01-AC5: document `{'price': 10}` with `multiply('price', 1)` applied → `doc['price']` equals 10 (boundary: identity factor).

Notes: S1 and S3 establish the name and the usage. The in-place semantics and the int/float factor domain are ASM-01 and ASM-02. The tolerance of 1e-9 is ASM-05 and relates to Q-08. Related: RSK-01.

### FR-02: Apply multiplication only to matching documents through `db.update`
Actor: ACT-01
Statement: WHEN `db.update(multiply(field, factor), query)` is called, the system SHALL apply the multiplication to each document matching `query` and to no other document.
Source: STATED (S3) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: table containing `{'category': 'books', 'price': 10}` and `{'category': 'toys', 'price': 10}`, with `db.update(multiply('price', 1.1), where('category') == 'books')` → the books document has price equal to 11.0 within 1e-9, and the toys document still has price 10.
- FR-02-AC2: table where no document matches the query, with `db.update(multiply('price', 1.1), where('category') == 'games')` → the call completes without raising an exception and every document's price is unchanged (boundary: empty match).
- FR-02-AC3: table containing one matching document with `price` 10 and one matching document with `price` 20, with `db.update(multiply('price', 2), where('category') == 'books')` → the two prices become 20 and 40 (boundary: multiple matches).

Notes: The query scoping is STATED by the S3 example. The behaviour is the same as for the existing update operations (`set`, `add`), which is an INFERRED reading of the existing update path. No P1 or P2 question blocks this requirement.

### FR-03: Failure cases for missing or non-numeric values
Actor: ACT-01
Statement: IF the target field is missing, or its value or the factor is not a number, THEN the system SHALL raise an exception and leave the document unchanged.
Source: ASSUMED (ASM-03), by analogy with the existing operations in `tinydb/operations.py` | Readiness: NEEDS-CLARIFICATION (Q-01, Q-02, Q-03, Q-06)
Acceptance criteria:
- FR-03-AC1: document `{'name': 'x'}` with `multiply('price', 1.1)` applied → a `KeyError` is raised and the document is unchanged (failure: missing field; see Q-02).
- FR-03-AC2: document `{'price': '10'}` with `multiply('price', 1.1)` applied → a `TypeError` is raised and `doc['price']` is still `'10'` (failure: string value; see Q-01).
- FR-03-AC3: `multiply('price', '1.1')` called with a string factor → a `TypeError` is raised by the `multiply` call itself (failure: non-numeric factor; see Q-06).
- FR-03-AC4: document `{'flag': True}` with `multiply('flag', 2)` applied → a `TypeError` is raised and `doc['flag']` is still `True` (boundary: bool is a Python int subclass; see Q-03).

Notes: The exception types and the "unchanged" outcome are ASSUMED. S1 and S4 do not state them. Q-01 asks whether a string should be repeated (Python `*`) instead. A partial failure inside one `db.update` call is not specified (see RSK-02).

## 6. Non-functional requirements

None identified. The input states no measurable quality for this operation. The float tolerance used in FR-01-AC1 is ASM-05 and is open under Q-08.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The operation SHALL take the field name first and the factor second, in the same style as the existing operations. | STATED (S4) |
| CON-02 | The operation SHALL be importable as `from tinydb.operations import multiply`. | STATED (S3) |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | `db.update(transform, query)` in `tinydb/table.py` accepts a transform callable and a query. | STATED (S3 usage example) | The operation cannot be used as requested; FR-02 would fail. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Float arithmetic gives results such as 10.999999999999998 instead of 11, so stored prices are not exact decimals. | S3 (factor 1.1 is a float); Q-08 | Users who compare stored prices for equality get surprises. | Answer Q-08. Document that results are float. Tests use a tolerance (ASM-05). |
| RSK-02 | If Q-01 is answered as "repeat the string", a string field is changed silently instead of raising. | Q-01 | Silent data corruption in string fields. | Answer Q-01 before implementation. Add the failure test from FR-03-AC2 either way. |

## 10. External evidence log

No external evidence was needed. The input names no law, regulation, standard, product or external system, and makes no numeric claim about the outside world. The factor `1.1` is a business example, not an external fact. The fetch tool was not called.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | — | — | — | — | — | — | — |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | S1, S3, S4; ASM-01 | Q-04, Q-08; ASM-02, ASM-05 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | S3; DEP-01 | None open (no P1/P2) | READY |
| FR-03 | ACT-01 | ASM-03 | Q-01, Q-02, Q-03, Q-06 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S2, S3) | — | Needs confirmation |
| CON-01 | — | STATED (S4) | — | READY (constraint) |
| CON-02 | — | STATED (S3) | — | READY (constraint) |
| DEP-01 | — | STATED (S3) | — | READY (dependency) |
| ASM-01 to ASM-05 | — | ASSUMED | See Section 2 of the register | Unconfirmed |
| RSK-01, RSK-02 | — | Q-08, Q-01 | — | Open |

Assumptions register (in-spec summary):
- ASM-01: `multiply` returns a transform that mutates the document in place and returns None, like `add` and `subtract`. Affects FR-01, FR-02.
- ASM-02: The factor is an int or float. Strings and bools are not factors. Affects FR-01, FR-03.
- ASM-03: Failures raise an exception and leave the document unchanged. A missing field raises `KeyError`, as `subtract` does. Affects FR-03.
- ASM-04: Zero and negative factors are accepted. Affects FR-01-AC3, FR-01-AC4.
- ASM-05: Float results are compared with a tolerance of 1e-9. Affects FR-01-AC1, FR-02-AC1.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from issue #4. No stakeholder answers. Open questions Q-01 to Q-08 recorded. Assumptions ASM-01 to ASM-05 recorded. No conflicts (CNF) found. No external claims (CLM) found. |

Open questions (answer to unblock):
- Q-01 (P2): On a string field, should `multiply` repeat the string (Python `*`) or raise `TypeError`? Blocks FR-03-AC2. Ask: issue author or maintainer.
- Q-02 (P2): For a missing field, should the transform raise `KeyError` (as `subtract` does) or skip the document? Blocks FR-03-AC1. Ask: issue author or maintainer.
- Q-03 (P2): Should `bool` values count as numbers (Python treats `True` as 1) or be rejected? Blocks FR-03-AC4. Ask: issue author or maintainer.
- Q-04 (P3): Are zero and negative factors allowed, or rejected with `ValueError`? Blocks FR-01-AC3, FR-01-AC4. Ask: issue author.
- Q-05 (P3): Should `NaN`, `inf` or `None` factors be rejected? Blocks no current criterion; extends FR-03. Ask: maintainer.
- Q-06 (P3): Should a non-numeric factor be rejected when `multiply(...)` is called (eager) or when the transform is applied (lazy)? Blocks FR-03-AC3. Ask: maintainer.
- Q-07 (P3): Should `docs/usage.rst` and the module docstring list `multiply`? Blocks no requirement. Ask: maintainer.
- Q-08 (P3): Is a 1e-9 float tolerance acceptable for results, or must results be rounded to a fixed number of decimals? Blocks the threshold in FR-01-AC1. Ask: issue author.

Validation (summary): all requirements have a source label. No P1 questions are open, so the overall readiness is PARTIALLY READY, with FR-02 READY. Every acceptance criterion uses →. Every FR has an actor. No absolutes or conflicting statements found. The assumptions are labelled and not presented as STATED.

Escalations: none required. Open questions go to the issue author and the maintainer.