# Requirements Specification: tinydb `!=` with missing fields

Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Source: GitHub issue #1 of Aasrithakalluri/tinydb. Speaker: issue reporter (identity not verified). No stakeholder is available to answer questions, so open items are documented and the specification continues.

| S# | Sentence (verbatim unless marked paraphrased) | Maps to |
|---|---|---|
| S1 | Title: "`!=` skips documents that don't have the field, but `~(... == ...)` doesn't." | FR-01 (problem statement) |
| S2 | "I have a table of users where some records have no `nickname` at all." | ACT-01, Glossary |
| S3 | "I wanted everyone whose nickname is not "bob": `db.search(where('nickname') != 'bob')`" | FR-01, ACT-01 |
| S4 | "This only returns the users that *have* a nickname other than bob." | FR-01 (current behaviour, reported) |
| S5 | "Users without a `nickname` are silently left out." | FR-01 (current behaviour, reported) |
| S6 | "But when I write the same thing with `~`: `db.search(~(where('nickname') == 'bob'))`" | FR-01, ACT-01 |
| S7 | "I get the users without a nickname too." | FR-01 (current behaviour, reported) |
| S8 | "Same logical question, two different answers, which cost me an afternoon because I assumed they were equivalent." | No requirement (motivation only) |
| S9 | (paraphrased) The reporter expects `!=` to behave like the negation of `==`. A document with no such field is "not equal to bob" and is expected in the results. | FR-01, FR-02 |
| S10 | Example data: `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}`, `{'name': 'c'}` | FR-01-AC1 (fixture) |
| S11 | `db.search(where('nickname') != 'bob')  # I get only b, expected b and c` | FR-01 (reported result), CNF-01 |

## 2. Purpose and scope

**In scope**
- Behaviour of the `!=` query when the queried field is absent from a document. Source: STATED (S1, S9, S11).
- Consistency between `where(p) != v` and `~(where(p) == v)` for the same document. Source: STATED (S1, S9).
- Non-regression for documents where the field is present. Source: ASSUMED (ASM-01).

**Out of scope**
- Other comparison operators (`==`, `<`, `>=`, `exists`, `matches`, `search`, `test`). Source: ASSUMED (ASM-04). The input does not mention them.
- Query-cache design, storage formats, and performance. Source: ASSUMED (ASM-04). The input does not mention them.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| `!=` (inequality query) | STATED (S3, S9) | (a) A document without the field matches (reporter's expectation). (b) A document without the field does not match (current reported behaviour, S4–S5). | AMBIGUOUS | Q-02 |
| Missing field | INFERRED (S2: "no `nickname` at all") | (a) The key is absent from the document. (b) The key is absent or its value is `None`. Working meaning: (a), see ASM-02. | ASSUMED | Q-01 |
| Negation (`~`) | STATED (S6) | Logical NOT of the query result for the same document. | CLEAR | None |
| Path that cannot be resolved | INFERRED (S9 applied to nested paths) | A parent key is absent, or an intermediate value is not a mapping (for example `{'profile': 5}` queried for `['profile']['nick']`). Options: (a) treated like a missing field (matches for `!=`). (b) treated as not matching for `!=`. | AMBIGUOUS | Q-01 |
| Table | STATED (S2) | A TinyDB table of documents (dicts). | CLEAR | None |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer using the tinydb query API | Writes `where(...)` queries with `!=`, `==` and `~` against a table (S3, S6). | STATED (S3, S6) |
| ACT-02 | tinydb maintainers | Decide the intended `!=` behaviour for missing fields (Q-02, CNF-01). No FR is linked because this actor decides rather than uses the system. | INFERRED (the issue is a bug report against the library, so the library's maintainers own the decision). |

## 5. Functional requirements

### FR-01: `!=` matches documents where the queried field is absent
Actor: ACT-01
Statement: IF a document does not contain the key queried by `where(<key>) != <value>`, THEN the system SHALL evaluate the query as a match for that document.
Source: STATED (S1, S9, S11) | Readiness: BLOCKED (CNF-01; Q-02 P1 open)
Acceptance criteria:
- FR-01-AC1: a table holds `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}` and `{'name': 'c'}`, and the developer runs `db.search(where('nickname') != 'bob')` → the result is exactly the documents named `b` and `c`.
- FR-01-AC2: a document `{'name': 'c'}` with no `nickname` key, and the query `where('nickname') != 'bob'` called on that document → the call returns `True`.
- FR-01-AC3 (boundary): a document `{'nickname': 'bob'}` and the query `where('nickname') != 'bob'` → the call returns `False`.
- FR-01-AC4 (failure or equivalence): the same three-document table, and both `db.search(where('nickname') != 'bob')` and `db.search(~(where('nickname') == 'bob'))` → both calls return the same set of documents (`b` and `c`).

Notes: CNF-01 records the conflict between S9 and the current behaviour. The current `Query.__ne__` (tinydb/queries.py, lines 267–278) uses `_generate_test`, which returns `False` when the path lookup raises `KeyError` or `TypeError` (lines 235–247). This was read from the code, not executed. Related: CNF-01, Q-02, ASM-02, RSK-01.

### FR-02: `!=` on an unresolvable path matches, as the negation of `==` does
Actor: ACT-01
Statement: IF the path of `where(<path>) != <value>` cannot be resolved in a document because a parent key is absent or an intermediate value is not a mapping, THEN the system SHALL evaluate the query as a match for that document, the same result as `not (where(<path>) == <value>)` gives for that document.
Source: INFERRED (S9 generalised to nested paths; needs confirmation) | Readiness: NEEDS-CLARIFICATION (Q-01 P2; Q-02 P1; depends on CNF-01)
Acceptance criteria:
- FR-02-AC1: a document `{'name': 'd'}` with no `profile` key, and the query `where('profile')['nick'] != 'bob'` → the call returns `True`, equal to the result of `~(where('profile')['nick'] == 'bob')` on the same document.
- FR-02-AC2 (failure case): a document `{'profile': 5}` where `profile` is not a mapping, and the query `where('profile')['nick'] != 'bob'` → the call returns `True`, equal to the negated `==` query result on the same document.
- FR-02-AC3 (boundary): a document `{'profile': {'nick': 'bob'}}` and the query `where('profile')['nick'] != 'bob'` → the call returns `False`.

Notes: Q-01 decides whether FR-02 applies at all (see option (b) in Section 3). If Q-01 selects option (b), FR-02 is SUPERSEDED. Related: Q-01, RSK-02.

### FR-03: `!=` keeps its current result when the field is present
Actor: ACT-01
Statement: WHILE the queried key is present in a document, the system SHALL evaluate `where(<key>) != <value>` exactly as it does before this change.
Source: ASSUMED (ASM-01) | Readiness: NEEDS-CLARIFICATION (ASM-01 unconfirmed; Q-02 P1 open)
Acceptance criteria:
- FR-03-AC1: a document `{'nickname': 'al'}` and the query `where('nickname') != 'bob'` → the call returns `True`.
- FR-03-AC2 (boundary): a document `{'nickname': None}` (field present, value `None`) and the query `where('nickname') != 'bob'` → the call returns `True`.
- FR-03-AC3 (boundary): a document `{'tags': [0, 1]}` and the query `where('tags') != [0, 1]` → the call returns `False`.

Notes: The issue reports only the missing-field case. FR-03 keeps the change narrow. Related: ASM-01, RSK-01.

## 6. Non-functional requirements

None identified. The input states no performance, security, availability or compatibility metric. Compatibility risk is recorded as RSK-01 and Q-02.

## 7. Constraints

None identified. The input states no deadline, budget, platform or mandated technology.

## 8. Dependencies

None identified. The input names no external system, service or data source.

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | Existing code that relies on `!=` excluding documents without the field changes its results without raising an error. | CNF-01; Q-02; S4–S5 | Silent change in search results for current users. | Maintainers decide under Q-02. Record the change in the change log and release notes. Add tests for present and absent fields (FR-01, FR-03). |
| RSK-02 | Applying the rule to nested or non-mapping paths (FR-02) changes more results than the reporter asked for. | Q-01; S9 | Broader behaviour change than the reported case. | Resolve Q-01 before FR-02 is marked READY. |

## 10. External evidence log

None identified. No fetch call was made. The issue cites no law, standard, named product or numeric external claim. The repository was read with Read and Grep only (not a web source). No code was executed, so the reported behaviour is not reproduced here.

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | None | None | None | None | None | None | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S9, S11) | CNF-01, Q-02, ASM-02 | BLOCKED |
| FR-02 | ACT-01 | INFERRED (S9) | Q-01, Q-02, CNF-01, ASM-02 | NEEDS-CLARIFICATION |
| FR-03 | ACT-01 | ASSUMED (ASM-01) | Q-02, ASM-01 | NEEDS-CLARIFICATION |
| ACT-01 | n/a | STATED (S3, S6) | n/a | n/a |
| ACT-02 | n/a | INFERRED | Q-02, CNF-01 | n/a |
| NFR (none) | n/a | n/a | n/a | n/a |
| CON (none) | n/a | n/a | n/a | n/a |
| DEP (none) | n/a | n/a | n/a | n/a |

## 12. Change log

- 0.1 (2026-11-22): Initial draft from issue #1. Open questions Q-01 and Q-02 and conflict CNF-01 are unresolved. Overall readiness is NOT READY.

---

## Open questions

| Q | Question | Why it matters | Blocks | Priority | Ask whom | Status | Answer |
|---|---|---|---|---|---|---|---|
| Q-01 | For a path whose parent key is absent or whose intermediate value is not a mapping (for example `where('profile')['nick'] != 'bob'` on `{'profile': 5}`), should `!=` return `True` (option a, same as the negation of `==`) or `False` (option b)? | Determines whether FR-02 applies and how far the change reaches. | FR-02, ASM-02 | P2 | tinydb maintainers | Open | |
| Q-02 | Should `!=` change its public behaviour so that documents without the field match? Options: (a) change `!=` to match the reporter's expectation (a breaking change for current users); (b) keep `!=` as it is and document `~(== ...)` as the negation-consistent form; (c) add a separate operator or flag. | This decides whether any fix is made. It also decides the behaviour of FR-01 and FR-03. | FR-01, FR-03, ASM-01, CNF-01, RSK-01 | P1 | tinydb maintainers (repository owner) | Open | |

## Assumptions

| ASM | Assumption | Basis | Affects | Risk if wrong | Status |
|---|---|---|---|---|---|
| ASM-01 | Results of `!=` for documents where the field is present do not change. | The issue reports only the missing-field case (S4–S7, S11). | FR-03 | Unrelated query results change. | Unconfirmed |
| ASM-02 | "Missing field" means the key is absent from the document mapping. A field whose value is `None` counts as present. | S2 ("no `nickname` at all"). Current behaviour already returns `True` for `None != 'bob'`. | FR-01, FR-03 | Documents with `None` values are handled differently from what the user expects. | Unconfirmed |
| ASM-03 | The issue's expected behaviour is the library's intended behaviour, not only this reporter's. | Filed as a bug against the tinydb repository. | FR-01 | The request is a feature change that needs a different design. | Unconfirmed |
| ASM-04 | Other comparison operators and the query-cache design are out of scope. | The input does not mention them. | Scope (Section 2) | Related operators behave inconsistently after the change. | Unconfirmed |

## Conflicts

| CNF | Statement A (source) | Statement B (source) | Affects | Who decides | Status |
|---|---|---|---|---|---|
| CNF-01 | The reporter expects `!=` to match a document without the field, as the negation of `==` does (S9). | The current `Query.__ne__` returns `False` when the path cannot be resolved (tinydb/queries.py lines 235–247, 267–278). The reporter observes that output (S4–S5, S11). | FR-01, FR-02, FR-03 | tinydb maintainers (Q-02) | Open. FR-01 is BLOCKED. |

## Unverified claims

None identified. The issue makes no external factual claim, so no CLM entries were raised and no fetch call was made.

## Escalations to a human

| Item | Reason | Needed from |
|---|---|---|
| Q-02 / CNF-01 | Changing `!=` is a public behaviour change that breaks existing queries. This needs a maintainer decision before any requirement can be READY. | tinydb maintainers (repository owner) |
| Q-01 | Defines the reach of the change for nested and non-mapping paths. | tinydb maintainers |

---

# Validation Summary: tinydb `!=` with missing fields

Overall readiness: NOT READY (P1 question Q-02 is open, and FR-01 is BLOCKED by CNF-01).

## 1. Counts
- Requirements: READY 0 | NEEDS-CLARIFICATION 2 (FR-02, FR-03) | BLOCKED 1 (FR-01)
- Questions: P1 1 (Q-02) | P2 1 (Q-01) | P3 0
- Assumptions: 4 (ASM-01 to ASM-04), all unconfirmed
- Conflicts: 1 (CNF-01)
- Claims: 0

## 2. Check results

| Check | Result | Details |
|---|---|---|
| V1 Every S# traced | PASS | S1–S11 are mapped in Section 1. S8 is marked "no requirement". |
| V2 Gap dimensions covered | PASS | Users (ACT-01, ACT-02), capabilities (FR-01–03), edge cases (FR-02, FR-03), compatibility (RSK-01, Q-02). Other dimensions are stated as "None identified" or are out of scope. |
| V3 Files and sections present | PASS | Sections 1–12 are present in the specification. The other two register files are not produced in this run (pipeline adaptation). |
| V4 No contradictions unrecorded | PASS | The S9 and current-behaviour conflict is recorded as CNF-01. |
| V5 IDs unique, labels valid | PASS | No duplicate IDs. Labels are from the allowed set. |
| V6 Traceability | PASS | Every FR has an actor and a source label. Every question lists what it blocks. |
| V7 Feasibility | PASS | No infeasible combination found. The compatibility risk is recorded as RSK-01. |
| V8 Testability | PASS | Each FR has at least 2 criteria, including a boundary or failure case. No NFR is stated. |
| V9 Honesty of numbers and policies | PASS | No numbers or policies are introduced beyond the input. |
| V10 No inferred item marked READY | PASS | FR-02 (INFERRED) and FR-03 (ASSUMED) are not READY. |

## 3. Ready vs not ready
- READY: none
- NEEDS-CLARIFICATION: FR-02, FR-03
- BLOCKED: FR-01

## 4. Evidence boundaries
- STATED: S1, S2, S3, S4, S5, S6, S7, S9 (paraphrased), S10, S11. ACT-01.
- EXTERNAL: none.
- Needs confirmation: FR-02 (INFERRED), ACT-02 (INFERRED), FR-03 (ASSUMED), ASM-01 to ASM-04, Q-01, Q-02, CNF-01.

## 5. Tool usage
No fetch call was made, because the issue cites no law, standard, named product or numeric external claim. The repository was read with Read and Grep to confirm the current `!=` and `~` code path. No code was executed, so the reported behaviour was not reproduced.

## 6. Limitations of this specification
- The reported behaviour comes from code reading and the issue text. It was not executed.
- No stakeholder answered. Q-01 and Q-02 remain open.
- The register files (assumptions-open-questions.md and validation-summary.md) are not written as separate files in this run. Their content is included in this specification.
- Compatibility impact on existing users is not measured.

## 7. Next actions
1. Q-02 (P1): maintainers decide whether `!=` changes for documents without the field, or whether the behaviour is kept and documented. Until this is answered, FR-01 stays BLOCKED.
2. Q-01 (P2): maintainers decide the behaviour for nested and non-mapping paths. This determines whether FR-02 is in scope.
3. ASM-01 and ASM-02: maintainers confirm the non-regression scope for present fields and the definition of "missing field".