# Requirements Specification: tinydb `multiply` update operation
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue author): "There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number."
- S2 (issue author): "I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time."
- S3 (issue author): "Would be great to have: `from tinydb.operations import multiply` / `db.update(multiply('price', 1.1), where('category') == 'books')`"
- S4 (issue author): "Same style as the other operations (takes the field name and the factor)."

## 2. Purpose and scope
- In scope: a ready-made update operation `multiply(field, n)` in `tinydb.operations` that multiplies a document field by a factor, used with `Table.update` (S1, S3, S4).
- Out of scope: other arithmetic (divide, percentage helpers), rounding or currency handling, and changes to the query or storage layers. Source: INFERRED from S4 (same style as existing operations) and the single-operation scope of the issue.

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "scale a number" | S1 | Multiply a numeric field by a factor (chosen) | ASSUMED (ASM-01) | Q-01 |
| factor `n` | S3, S4 | Int or float, as in `add`/`subtract` signatures | ASSUMED (ASM-02) | Q-02 |
| non-numeric field | not stated | Raise error (chosen) vs. other behaviour | ASSUMED (ASM-03) | Q-03 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Calls `Table.update` with the operation (S3) | STATED (S3) |

## 5. Functional requirements

### FR-01: Multiply a numeric field by a factor
Actor: ACT-01
Statement: WHEN `Table.update` is called with `multiply(field, n)` and a query, the system SHALL multiply the value of `field` in each matching document by `n` and store the result.
Source: STATED (S1, S3, S4) | Readiness: NEEDS-CLARIFICATION (Q-01, Q-02, Q-03)
Acceptance criteria:
- FR-01-AC1: a matching document with `price` 10 and `multiply('price', 1.1)` applied → `price` equals 11.0 (within float tolerance)
- FR-01-AC2: a matching document with `price` 7 and factor 1 → `price` stays 7; with factor 0 → `price` becomes 0 (boundary values)
- FR-01-AC3: a matching document whose `price` is the string `'ten'` and factor 1.5 → `TypeError` is raised and the stored `price` remains `'ten'` (failure case)
- FR-01-AC4: a matching document without the field `cost` and `multiply('cost', 2)` applied → `KeyError` is raised and the stored document is unchanged (failure case)
Notes: Behaviour for int factors on string values (string repetition, e.g. `'ten' * 2`) is Python's default and is not specified here; see RSK-01. Related: Q-03.

## 6. Non-functional requirements
None identified. (Performance and scale are not stated; not invented.) Q-04 (P3) asks whether a performance target is needed.

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The operation must follow the style of existing operations in `tinydb/operations.py` (factory function returning a transform; no package imports) | STATED (S4) and ARCHITECTURE.md section 1 (component 7) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | `Table.update` accepts an operation callable (existing API) | EXTERNAL (repository code, `tests/test_operations.py`) | Operation cannot be used |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Int factor on a string field silently repeats the string | Q-03 | Wrong data stored without error | Ask Q-03; add a type check if required |
| RSK-02 | Float results are not exact (e.g. 10 × 1.1) | S2 | Equality checks on prices may fail | Document; callers round as needed |

## 10. External evidence log
None: no external fact (law, standard, product capability) is involved. No fetch call was made.

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | S1, S3, S4 | Q-01, Q-02, Q-03 | NEEDS-CLARIFICATION |
| ACT-01 | — | S3 | — | — |
| CON-01 | — | S4 | — | — |
| DEP-01 | — | EXTERNAL (repo code) | — | — |

## 12. Change log
- 0.1 (2026-11-22): initial draft from issue #4. Open questions kept open; no stakeholder available.