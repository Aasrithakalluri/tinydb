# Requirements Specification: TinyDB issue #1, `!=` on documents without the field

Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY (P1 question Q-01 is open)

## 1. Input record

Source: GitHub issue #1 in Aasrithakalluri/tinydb. Speaker: issue reporter (unnamed GitHub user). No stakeholder is available to answer questions in this pipeline run.

- S1: Title: "`!=` skips documents that don't have the field, but `~(... == ...)` doesn't."
- S2: "I have a table of users where some records have no `nickname` at all."
- S3: "I wanted everyone whose nickname is not "bob"," shown as `db.search(where('nickname') != 'bob')`.
- S4: "This only returns the users that *have* a nickname other than bob."
- S5: "Users without a `nickname` are silently left out."
- S6: "But when I write the same thing with `~`," shown as `db.search(~(where('nickname') == 'bob'))`, "I get the users without a nickname too."
- S7: "Same logical question, two different answers, which cost me an afternoon because I assumed they were equivalent."
- S8: "I'd expect `!=` to behave like the negation of `==`: a document that has no such field is 'not equal to bob', so it is expected to be returned."
- S9: Example: insert `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}`, `{'name': 'c'}`. Then `search(where('nickname') != 'bob')` returns only b; the reporter expects b and c.

Code inspection (not an S#, recorded as EV-01): `tinydb/queries.py` lines 235–247 resolve the path inside `runner()`. A `KeyError` or `TypeError` returns `False` before the test runs. `__ne__` (lines 267–278) uses that runner, so `!=` is `False` for a missing key. `__invert__` (lines 136–138) negates the result, so `~(== ...)` is `True` for a missing key. The current behaviour therefore matches the report.

## 2. Purpose and scope

**In scope:**
- The `!=` query operator (`Query.__ne__`) applied to a document field, including nested paths. Source: S1, S3, S8.
- Keeping `==` and `~` results unchanged. Source: INFERRED from S8 ("behave like the negation of `==`"). Needs confirmation.

**Out of scope:**
- Changing `==`, `~`, `<`, `>`, `one_of`, `any`, `all`, `test`, `matches`, `search`, or `fragment` semantics. Source: ASSUMED (ASM-03); the issue names only `!=`, `==` and `~`.
- Storage backends, the query cache, and documentation changes. Source: ASSUMED (ASM-03).

**Open questions:**
- Q-01 (P1): Should the change be made as a behaviour change in the library, which alters results for every existing `!=` query on documents with missing fields? Ask: project maintainers. Blocks FR-01, FR-02.
- Q-02 (P2): For a nested path where an intermediate value is not a dict (for example `where('profile').nickname` when `profile` is a string or missing), should `!=` return `True`, as `~(==)` does today? Options: (a) yes, treat the same as a missing key; (b) keep `False`. Blocks FR-02.
- Q-03 (P3): Does a field present with value `None` count as "has the field"? Current behaviour is `None != 'bob'` → `True`, and this specification keeps it. Blocks nothing; confirms the glossary entry.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "has the field" / "no such field" | S5, S8 | (a) the key is absent from the document; (b) the key is present with value `None`. ASM-01 uses (a). | AMBIGUOUS (resolved for this spec by ASM-01) | Q-03 |
| "not equal" | S8 | Defined as the negation of `==` for the same path and value, per S8. | STATED (S8) | — |
| "negation" | S8 | Logical NOT of the `==` query result, that is `~(q == v)`. | STATED (S8) | — |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | Builds TinyDB queries with `where(...)` or `Query()` and calls `search`, `count`, or other query-based methods. | INFERRED (S3, S9: the reporter writes queries against a table). Needs confirmation. |
| ACT-02 | Issue reporter | GitHub user who reported the behaviour. Not a system user. | STATED (S2, S7) |

## 5. Functional requirements

### FR-01: `!=` matches documents where the field is absent
Actor: ACT-01
Statement: WHEN a query `where(path) != value` is evaluated against a document in which the key at `path` is absent, the system SHALL include the document in the result (the test returns `True`).
Source: STATED (S8, S9) | Readiness: NEEDS-CLARIFICATION (Q-01 P1; ASM-01)
Acceptance criteria:
- FR-01-AC1: Table contains `{'name':'a','nickname':'bob'}`, `{'name':'b','nickname':'al'}`, `{'name':'c'}`; `search(where('nickname') != 'bob')` → returns the documents for b and c, in insertion order.
- FR-01-AC2: `Query().nickname != 'bob'` applied to `{'name':'c'}` → returns `True`.
- FR-01-AC3 (failure/negative case): `Query().nickname != 'bob'` applied to `{'nickname':'bob'}` → returns `False`.
- FR-01-AC4 (boundary): `Query().nickname != 'bob'` applied to `{'nickname': None}` → returns `True`, unchanged from current behaviour (Q-03).
Notes: EV-01 (current code returns `False` for a missing key). Related: ASM-01, Q-01, RSK-01.

### FR-02: `!=` equals the negation of `==` for every document
Actor: ACT-01
Statement: WHEN a query `where(path) != value` is evaluated against any document, the system SHALL return the same boolean result as `~(where(path) == value)` for that document.
Source: STATED (S1, S8) | Readiness: NEEDS-CLARIFICATION (Q-02 P2; Q-01 P1)
Acceptance criteria:
- FR-02-AC1: For documents `{'nickname':'bob'}`, `{'nickname':'al'}`, `{'name':'c'}`, and `Q = where('nickname')`; for each document, `(Q != 'bob')(doc)` equals `(~(Q == 'bob'))(doc)` → holds for all three documents.
- FR-02-AC2 (boundary, nested path): `Q = where('profile').nickname`, document `{'profile': 'text'}`; `(Q != 'bob')(doc)` equals `(~(Q == 'bob'))(doc)` → holds, with both returning `True` if Q-02 option (a) is chosen; the expected value is TBD (Q-02).
- FR-02-AC3 (failure case): `Query().value != [0, 1]` applied to `{'value': [0, 1]}` → returns `False`, matching `~(Query().value == [0, 1])` returning `True`... expected `!=` result stays `False` (unchanged).
Notes: AC2 result depends on Q-02. AC3 restates the existing test in `tests/test_queries.py` lines 72–75. Related: EV-01.

### FR-03: `==` and `~` results for missing fields are unchanged
Actor: ACT-01
Statement: WHEN a query `where(path) == value` is evaluated against a document in which the key at `path` is absent, the system SHALL return `False`, and `~` of that query SHALL return `True`.
Source: INFERRED (S8: `!=` is to match the negation of `==`, so `==` is the reference). Needs confirmation. | Readiness: NEEDS-CLARIFICATION (ASM-01)
Acceptance criteria:
- FR-03-AC1: `Query().nickname == 'bob'` applied to `{'name':'c'}` → returns `False`.
- FR-03-AC2: `~(Query().nickname == 'bob')` applied to `{'name':'c'}` → returns `True`.
- FR-03-AC3 (boundary): `Query().nickname == 'bob'` applied to `{'nickname':'bob'}` → returns `True`.
Notes: Regression guard. Related: ASM-01, EV-01.

## 6. Non-functional requirements

None identified. The issue states no performance, availability, or other quality target. Any NFR would need a metric from a stakeholder (TBD, not invented here).

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| — | None identified. The issue states no deadline, budget, platform, or mandated technology. | — |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| — | None identified. The change is internal to the query module and needs no external system. | — | — |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Existing user code that relies on `!=` excluding documents with a missing field changes its results. | S5 (current behaviour is a reported surprise), Q-01 | Silent change in query results after upgrade | Maintainers decide (Q-01); record in release notes if accepted. |
| RSK-02 | Nested-path behaviour (Q-02) is changed for one case but not the other, so `!=` and `~(==)` still differ on non-dict intermediates. | Q-02 | FR-02 not fully met | Resolve Q-02 before implementation; add FR-02-AC2 as a test. |

**Escalations (human decision needed):**
- Q-01: Project maintainers must decide whether changing `!=` is an accepted behaviour change. Needed from: TinyDB maintainers.
- Q-02: Maintainers must choose the nested-path rule. Needed from: TinyDB maintainers.

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| EV-01 | Does the current `!=` return `True` for a missing key? (local code inspection, not an external source) | Local file `tinydb/queries.py` lines 235–278 and 136–138 | 2026-11-22 | `runner()` returns `False` on `KeyError`/`TypeError` before the test runs; `__ne__` uses that runner; `__invert__` negates. The current `!=` on a missing key is `False`, and `~(==)` is `True`. | SUPPORTS (reported behaviour reproduced by reading code; not executed) | FR-01, FR-02, FR-03 | None. Records the baseline. |

No external web or fetch calls were made. This is a code-behaviour issue with no law, standard, or product claim (see Section 11).

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S8, S9) | Q-01 (P1), ASM-01, EV-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S1, S8) | Q-01 (P1), Q-02 (P2), EV-01 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | INFERRED (S8) | ASM-01, EV-01 | NEEDS-CLARIFICATION |
| ACT-01 | — | INFERRED (S3, S9) | — | — |
| ACT-02 | — | STATED (S2, S7) | — | — |
| ASM-01 | — | ASSUMED: `!=` on an absent key returns `True`, and `!=` equals `~(==)` for the same path and value. | FR-01 to FR-03 | — |
| ASM-02 | — | ASSUMED: a present field with value `None` keeps current behaviour. | Q-03 | — |
| ASM-03 | — | ASSUMED: only the `!=` operator changes; other operators are out of scope. | Section 2 | — |
| Q-01 (P1) | — | Open | FR-01, FR-02 | — |
| Q-02 (P2) | — | Open | FR-02 | — |
| Q-03 (P3) | — | Open | FR-01-AC4 | — |
| RSK-01, RSK-02 | — | Section 9 | Q-01, Q-02 | — |

**Readiness summary:** READY: 0. NEEDS-CLARIFICATION: 3 (FR-01, FR-02, FR-03). BLOCKED: 0.

## 12. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-22 | Initial specification from issue #1. Interpretation of the issue is ASSUMED (ASM-01): `!=` on an absent key returns `True`. Current behaviour verified by code reading (EV-01). Open: Q-01 (P1), Q-02 (P2), Q-03 (P3). No stakeholder answers available. |