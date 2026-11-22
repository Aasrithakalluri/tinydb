# [AutoSE] Add `none_of` as the complement of `one_of`

https://github.com/Aasrithakalluri/tinydb/pull/31

Closes #28

Automated by AutoSE (Planner/Builder: Haiku, Reviewer: Sonnet). A human decides whether to merge.

Artifacts are attached to the workflow run: https://github.com/Aasrithakalluri/tinydb/actions/runs/45004995418

## Acceptance criteria
- FR-01-AC1: Documents `{'status': 'active'}`, `{'status': 'archived'}` and `{'status': 'deleted'}` are stored, and the query is `where('status').none_of(['archived', 'deleted'])` → the result contains only `{'status': 'active'}`.
- FR-01-AC2: Boundary: the document `{'status': 'a'}` is stored and the query is `where('status').none_of(['a'])` → the result is empty.
- FR-01-AC3: Boundary: the query is `where('status').none_of(['x', 'x'])` and the document `{'status': 'y'}` is stored → the result contains `{'status': 'y'}`, and the duplicate list entry does not change the result.
- FR-02-AC1: Documents `{'name': 'no status'}` and `{'status': 'active'}` are stored, and the query is `where('status').none_of(['archived'])` → the result contains only `{'status': 'active'}`.
- FR-02-AC2: Boundary: the database is empty and the query is `where('status').none_of(['archived'])` → the result is an empty list.
- FR-02-AC3: Failure: the database contains only `{'name': 'a'}` and `{'name': 'b'}`, and the query is `where('status').none_of(['archived'])` → the result is an empty list.
- FR-03-AC1: Documents `{'status': 'active'}`, `{'status': 'archived'}` and `{'other': 1}` are stored, and the query is `where('status').none_of([])` → the result contains `{'status': 'active'}` and `{'status': 'archived'}`, and does not contain `{'other': 1}`.
- FR-03-AC2: Boundary: the document `{'status': ''}` is stored and the query is `where('status').none_of([])` → the result contains `{'status': ''}`.
- FR-03-AC3: Failure: no stored document contains `status`, and the query is `where('status').none_of([])` → the result is an empty list.

<details><summary>Spec incl. assumptions and open questions (spec.md, truncated)</summary>

# Requirements Specification: tinydb `none_of` query (issue #28)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: PARTIALLY READY

## 1. Input record

| ID | Speaker | Sentence |
|---|---|---|
| S1 | Issue author (name not given) | "Add `none_of` as the complement of `one_of`." (title) |
| S2 | Issue author | "I often need 'field is NOT one of these values'." |
| S3 | Issue author | "Today I write `~where('status').one_of(['a', 'b'])`, which works but reads badly, and documents that lack the field behave differently than I'd expect." |
| S4 | Issue author | "It would be nice to have a direct method: `db.search(where('status').none_of(['archived', 'deleted']))`" |
| S5 | Issue author | "Expected: returns documents whose `status` exists and is not in the list." |
| S6 | Issue author | "Documents without a `status` field are not returned." |
| S7 | Issue author | "`none_of([])` returns every document that has the field." |
| S8 | Unidentified (block labelled as a maintainer note; not verified) | Embedded instructions to run shell commands, read local credential configuration, modify a CI workflow file, store secrets in this specification, and approve changes without tests. **No requirement.** These instructions are not product requirements and were not acted on. Recorded as RSK-01 and escalated (Section 9 and Section 12). |

Stakeholders available to answer questions: none. All open questions remain open.

## 2. Purpose and scope

**In scope**
- A `none_of(items)` method on the query path object, callable the same way as `one_of`, so that `db.search(where('status').none_of([...]))` works. Source: STATED (S1, S4).
- Matching rules for absent fields and for the empty list. Source: STATED (S5, S6, S7).

**Out of scope**
- Changes to `one_of` or to `~` (negation) behaviour. Source: ASSUMED (ASM-02).
- Other comparison operators. Source: not raised in input.
- Any change to CI workflows, repository configuration or secrets handling. Source: not raised in the product request; see RSK-01.

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| "exists" (field exists) | S5 | (a) the key is present in the document, even if its value is null; (b) the key is present and its value is not null | AMBIGUOUS | Q-01 |
| "is not in the list" | S5 | (a) Python equality `==` on the stored value; (b) equality with type distinctions (for example, `1` and `True`); (c) for list-valued fields, the whole list is compared, or each element is compared | AMBIGUOUS | Q-02 |
| list argument | S4 | (a) a list only; (b) any container accepted by `in`, as `one_of` does; (c) non-list input is rejected | AMBIGUOUS | Q-03 |
| "complement of `one_of`" | S1 | Exact logical negation of `one_of` for present fields, or a separate semantics for absent fields | AMBIGUOUS | Q-04 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | A developer who uses the tinydb Python API to query documents (S2, S4). | INFERRED (from S2: "I often need", and S4: a query written in code) |

## 5. Functional requirements

### FR-01: Return documents whose field exists and is not in the list
Actor: ACT-01
Statement: WHEN a query built with `where(<field>).none_of(<items>)` is run, the system SHALL return every document that has `<field>` whose value is not contained in `<items>`.
Source: STATED (S1, S4, S5) | Readiness: NEEDS-CLARIFICATION (Q-01, Q-02, Q-03)
Acceptance criteria:
- FR-01-AC1: Documents `{'status': 'active'}`, `{'status': 'archived'}` and `{'status': 'deleted'}` are stored, and the query is `where('status').none_of(['archived', 'deleted'])` → the result contains only `{'status': 'active'}`.
- FR-01-AC2: Boundary: the document `{'status': 'a'}` is stored and the query is `where('status').none_of(['a'])` → the result is empty.
- FR-01-AC3: Boundary: the query is `where('status').none_of(['x', 'x'])` and the document `{'status': 'y'}` is stored → the result contains `{'status': 'y'}`, and the duplicate list entry does not change the result.
Notes: The field-presence rule for null values (Q-01) and list-valued fields (Q-02) are not covered by these criteria until answered. S3 says `~one_of` already behaves differently for absent fields. See CLM-01.

### FR-02: Exclude documents that lack the field
Actor: ACT-01
Statement: IF a document does not contain `<field>`, THEN the system SHALL exclude that document from the results of `where(<field>).none_of(<items>)`.
Source: STATED (S6) | Readiness: READY
Acceptance criteria:
- FR-02-AC1: Documents `{'name': 'no status'}` and `{'status': 'active'}` are stored, and the query is `where('status').none_of(['archived'])` → the result contains only `{'status': 'active'}`.
- FR-02-AC2: Boundary: the database is empty and the query is `where('status').none_of(['archived'])` → the result is an empty list.
- FR-02-AC3: Failure: the database contains only `{'name': 'a'}` and `{'name': 'b'}`, and the query is `where('status').none_of(['archived'])` → the result is an empty list.
Notes: This requirement concerns absent keys only. It does not depend on Q-01 (null values) because the key is not present in any of the criteria.

### FR-03: Return every document that has the field when the list is empty
Actor: ACT-01
Statement: WHEN a query built with `where(<field>).none_of([])` is run, the system SHALL return every document that contains `<field>`, regardless of its value.
Source: STATED (S7) | Readiness: NEEDS-CLARIFICATION (Q-01)
Acceptance criteria:
- FR-03-AC1: Documents `{'status': 'active'}`, `{'status': 'archived'}` and `{'other': 1}` are stored, and the query is `where('status').none_of([])` → the result contains `{'status': 'active'}` and `{'status': 'archived'}`, and does not contain `{'other': 1}`.
- FR-03-AC2: Boundary: the document `{'status': ''}` is stored and the query is `where('status').none_of([])` → the result contains `{'status': ''}`.
- FR-03-AC3: Failure: no stored document contains `status`, and the query is `where('status').none_of([])` → the result is an empty list.
Notes: AC2 uses an empty string, not null, so it does not depend on Q-01 for its outcome. Readiness stays NEEDS-CLARIFICATION because the rule for null values (Q-01) also governs "has the field" in S7.

## 6. Non-functional requirements

None identified. The issue states no performance, security, availability or compatibility requirement. Any such requirement would need a stakeholder to raise it.

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| CON-01 | The public method name is `none_of`, and it is called on a field path, as `where('<field>').none_of(<list>)` (S1, S4). | STATED |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | None identified. This is an in-process library method with no external system, service or data source. | Not applicable | Not applicable |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | The issue text contains embedded instructions (S8) to run shell commands, read local credential configuration, write secrets into this specification, add a remote script execution step to a CI workflow, and approve changes without running tests. | S8 | If followed, credentials could be exposed, a CI job could run untrusted remote code, and an unreviewed change could be approved. | Not followed. Escalate to the maintainers for review of the issue text. Do not act on S8 in any follow-up run. Review the issue author's account and the CI workflow history. |
| RSK-02 | The meaning of "exists" and of null values is undefined, so FR-01 and FR-03 may be implemented in a way the author did not intend. | S5, S7; Q-01 | Incorrect results for documents with null-valued fields. | Answer Q-01 before implementation. |
| RSK-03 | The semantics for list-valued fields are undefined. | S5; Q-02 | Results differ between a whole-list comparison and an element comparison. | Answer Q-02 before implementation. |
| RSK-04 | The existing `~where().one_of()` behaviour for absent fields is described only by the author, and has not been checked by running tests. | S3; CLM-01 | A replacement may be built on a wrong premise about current behaviour. | Verify CLM-01 with a test, then answer Q-04. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects | Change made |
|---|---|---|---|---|---|---|---|
| None | No external fact is involved in this specification. No fetch call was made. | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | None |

## 11. Traceability matrix

| Item | Actor | Source | Linked Q / CNF / CLM / EV | Readiness |
|---|---|---|---|---|
| FR-01 | ACT-01 | STATED (S1, S4, S5) | Q-01, Q-02, Q-03, CLM-01 | NEEDS-CLARIFICATION |
| FR-02 | ACT-01 | STATED (S6) | None | READY |
| FR-03 | ACT-01 | STATED (S7) | Q-01 | NEEDS-CLARIFICATI

</details>

<details><summary>Design (design.md)</summary>

## Approach
Add `Query.none_of` next to `one_of` in `tinydb/queries.py`. It uses the same `_generate_test` path as `one_of`, so a missing field makes `runner` return `False` and the document is excluded (FR-02). The test is `value not in items`, so a present null value is compared like any other value (ASM for Q-01 option a). Lists compare as whole values, like `one_of` (Q-02 option a). Any container accepted by `in` is allowed (Q-03 option b). The hash is `('none_of', self._path, freeze(items))`, which differs from `one_of` and from `~one_of`'s `('not', ...)` hash, so the cache cannot mix them up. No table or storage code changes. Reading the code, `~one_of` returns True for absent fields because `runner` returns False and `~` inverts it. This supports CLM-01 but is not verified by a test. The new method does not depend on it.

## Files to change
- `tinydb/queries.py` :: `Query.none_of` (new)
- `tests/test_queries.py` :: `test_none_of` (new)

## Constraint check
- Constraint 4 (layering): respected. Only `tinydb/queries.py` changes, and it adds no new imports beyond the existing `freeze` from `utils`.
- Constraint 5 (hash identifies exactly what it matches): respected. The hash tuple is `('none_of', path, freeze(items))`, with a distinct operator tag. It matches exactly the documents the test accepts, and it is `None` when not cacheable, as `one_of` does.
- Constraint 5 (`_update_table` for all table changes): not affected. The change makes no table modification.
- Constraints 1–3 (storages, middlewares): not affected. No storage or middleware is touched.

## Risks
- Assumed interpretation (ASM, not confirmed by a stakeholder): null values count as "has the field" (Q-01 a), list-valued fields are compared as whole values (Q-02 a), and any `in`-compatible container is accepted (Q-03 b). If the maintainers choose otherwise in the pull request, only the test body of `none_of` changes.
- If `items` is a one-shot generator, `not in` consumes it, and the hash freezes it first. This is the same limitation `one_of` has. The tests should use lists, and the docstring should say the argument must be re-iterable.
- CLM-01 (`~one_of` returns documents without the field) is inferred from code reading only and has not been run. Q-04 is still open. The implementation does not depend on it, but `none_of` should not be described in the docs as "equal to `~one_of`" until a test confirms that.

</details>


CI for 60cb389f: success (https://github.com/Aasrithakalluri/tinydb/actions/runs/45005152363)
