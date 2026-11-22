# Requirements Specification: multiply update operation
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record
- S1 (issue author, GitHub issue #4): "There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number."
- S2 (issue author): "I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time."
- S3 (issue author): "db.update(multiply('price', 1.1), where('category') == 'books')"
- S4 (issue author): "Same style as the other operations (takes the field name and the factor)."

## 2. Purpose and scope
- In scope: a ready-made update operation `multiply(field, n)` in `tinydb.operations` that multiplies a document field by a factor, used with `Table.update`. Source: STATED (S1, S3, S4).
- Out of scope: non-numeric fields (strings, lists, None), type checking of the field value, and any change to other operations. Source: ASSUMED (ASM-01).

## 3. Glossary and ambiguous terms
| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| factor | STATED (S2, S4) | Numeric multiplier `n`; int or float | ASSUMED | Q-01 |
| same style | STATED (S4) | Matches `add`/`subtract`: takes field name and value, raises on missing field | ASSUMED | Q-02 |

## 4. Actors
| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Library user | Python developer who calls `db.update(multiply(...), query)` | INFERRED (S1, S3: the issue author uses TinyDB operations) |

## 5. Functional requirements

### FR-01: Multiply a numeric field by a factor
Actor: ACT-01
Statement: WHEN `multiply(field, n)` is applied to a document through `Table.update`, the system SHALL set the document's `field` to its previous value multiplied by `n`.
Source: STATED (S1, S3, S4) | Readiness: NEEDS-CLARIFICATION (Q-01, Q-02)
Acceptance criteria:
- FR-01-AC1: a document with int field `int` = 1 and the update `multiply('int', 3)` matched to it → the stored `int` value equals 3
- FR-01-AC2: a document with int field `int` = 1 and the update `multiply('int', 1.1)` matched to it → the stored `int` value equals 1.1 (approximately, float comparison)
- FR-01-AC3: a document with int field `int` = 1 and the update `multiply('int', 0)` matched to it → the stored `int` value equals 0 (boundary: zero factor)
- FR-01-AC4: a document without the field `int` and the operation `multiply('int', 2)` applied to it → a KeyError is raised and the document is unchanged (failure: missing field)

Notes: The issue gives an example, not a full spec. Behaviour for missing fields is ASSUMED to match `add`, `subtract`, `increment` (raise KeyError). See Q-02. Ask whether a factor of 0 or negative factors need special handling (Q-03). No external facts are involved, so no fetch was needed.

## 6. Non-functional requirements
None identified. (Performance and precision: TBD (Q-04). Floating-point results follow Python float arithmetic.)

## 7. Constraints
| ID | Constraint | Source label |
|---|---|---|
| CON-01 | `tinydb/operations.py` imports nothing from the package and adds no dependency | STATED (ARCHITECTURE.md section 1, component 7) |
| CON-02 | Updates go through `Table.update`, which clears the query cache | STATED (ARCHITECTURE.md section 3, rule 5) |

## 8. Dependencies
| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | `Table.update` in `tinydb/table.py` applies the transform to each matching document | INFERRED (existing `add`/`increment` usage) | Operation cannot be used |

## 9. Risks
| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | A non-numeric field value (for example a string) is multiplied without error, or raises TypeError | Out of scope (ASM-01) | Silent wrong data for string fields | Decide in Q-01 whether to guard types |
| RSK-02 | Floating-point results are inexact (for example 1.1 times 10) | Python float arithmetic | Price values may show rounding noise | Q-04 for rounding rules |

## 10. External evidence log
None (no external fact was involved; no fetch call was needed).

## 11. Traceability matrix
| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S3, S4) | Q-01, Q-02, Q-03 | NEEDS-CLARIFICATION |
| ACT-01 | - | INFERRED (S1, S3) | Q-02 | NEEDS-CLARIFICATION |
| CON-01 | - | STATED (ARCHITECTURE.md) | - | READY |
| CON-02 | - | STATED (ARCHITECTURE.md) | - | READY |
| DEP-01 | ACT-01 | INFERRED | - | NEEDS-CLARIFICATION |

## 12. Change log
- 0.1 (2026-11-22): first draft from GitHub issue #4.