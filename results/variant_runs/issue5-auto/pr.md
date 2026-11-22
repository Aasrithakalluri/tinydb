# [AutoSE] Results come back in a strange order

https://github.com/Aasrithakalluri/tinydb/pull/18

Closes #5

Automated by AutoSE (Planner/Builder: Haiku, Reviewer: Sonnet). A human decides whether to merge.

Artifacts are attached to the workflow run: https://github.com/Aasrithakalluri/tinydb/actions/runs/44996817878

## Acceptance criteria
- FR-01-AC1: a table has documents with IDs 1, 2, 3 inserted in that order, and document 1 is then updated with `update({'v': 9}, doc_ids=[1])` → `all()` returns documents with doc_id values [1, 2, 3] in that order.
- FR-01-AC2: a table has documents with IDs 1, 2, 3, and document 2 is removed with `remove(doc_ids=[2])` → `all()` returns doc_id values [1, 3].
- FR-01-AC3: a table with 12 inserted documents → `all()` returns doc_id values [1, 2, ..., 12] in numeric order, not lexical order (1, 10, 11, 12, 2, ...).
- FR-01-AC4: an empty table, or a table where every document has been removed → `all()` returns an empty list.
- FR-02-AC1: a table has documents with IDs 1, 2, 3 and `search(where('k') == 'x')` matches documents 3 and 1 → `search` returns doc_id values [1, 3].
- FR-02-AC2: the same search is called twice with no change between calls, with an update to document 1 between them that keeps it matching → the second call returns the same order as the first call, and the order matches the relative order from `all()`.
- FR-02-AC3: a search with no matching documents → `search` returns an empty list.
- FR-03-AC1: a JSON-backed database with 12 documents is created with default storage options, closed, and reopened from the same path → `all()` returns doc_id values [1, 2, ..., 12] in the same order as before the close.
- FR-03-AC2: a JSON-backed database has documents inserted, one updated and one removed, then is closed and reopened → `all()` after reopen returns the same doc_id sequence as `all()` immediately before close.
- FR-03-AC3: a JSON-backed database is reopened after a close with an empty file or with no table → `all()` returns an empty list.

<details><summary>Spec incl. assumptions and open questions (spec.md, truncated)</summary>

# Requirements Specification: tinydb result ordering (issue #5)
Version: 0.1 | Date: 2026-11-22 | Overall readiness: NOT READY

## 1. Input record

Speaker for all sentences: GitHub issue #5 reporter (unnamed). No stakeholder is available to answer questions.

| S# | Sentence |
|---|---|
| S1 | "Results come back in a strange order" |
| S2 | "Sometimes `db.all()` and `db.search(...)` give me documents in an order that doesn't look right." |
| S3 | "I don't know exactly when it happens, but it seems related to how I created or changed the documents." |
| S4 | "It also looks different after I close and reopen the program." |
| S5 | "I'd like the order to be sensible and predictable, so my page doesn't jump around." |

Scope check: this is a software problem (the tinydb Python library). No out-of-scope requests were found.

Repository observations (code reading only, not external evidence):
- `tinydb/table.py:235-247`: `Table.all()` returns `list(iter(self))`.
- `tinydb/table.py:732-742`: `Table.__iter__` iterates `_read_table()` in its stored order.
- `tinydb/table.py:249-297`: `Table.search()` builds results by iterating `_read_table()` in stored order and caches the list.
- `tinydb/table.py:779-802`: `_read_table()` returns the stored table dict without sorting.
- `tinydb/storages.py:147`: `JSONStorage.write` calls `json.dumps(data, **self.kwargs)`. The default kwargs are OPEN (Q-04).
- `tests/test_storages.py:33`: a test constructs TinyDB with `sort_keys=True`, which shows that sorted-key output is a configuration in use.

## 2. Purpose and scope

**In scope (ASSUMED, ASM-01 to ASM-04):**
- Defining and enforcing a deterministic order for `Table.all()` and `Table.search()` results.
- Keeping that order stable across document updates, removals and a close/reopen cycle of the database file.

**Out of scope (ASSUMED, pending Q-06):**
- Sorting by a user-specified field or adding a new sort parameter.
- Changing the order of `Table.get(cond)` beyond what is stated in its existing docstring.

Source for all scope items: S5 (STATED for the goal "sensible and predictable order"). The exact order rule is ASSUMED (see ASM-01).

## 3. Glossary and ambiguous terms

| Term | Source | Meaning or options | Status | Q |
|---|---|---|---|---|
| sensible | S5 | (a) insertion order; (b) ascending document ID; (c) most recently modified last; (d) user-chosen sort key | AMBIGUOUS | Q-01 |
| predictable | S5 | Same input history gives the same order every time (interpretation adopted: deterministic across runs and reopen) | AMBIGUOUS | Q-01 |
| jump around | S5 | Documents change position after an update, removal or reopen (interpretation adopted) | AMBIGUOUS | Q-01 |
| doesn't look right | S2 | Unspecified expected order | AMBIGUOUS | Q-01 |
| changed (documents) | S3 | Update, upsert, removal, or re-insert; each may affect order differently | AMBIGUOUS | Q-02 |
| different after reopen | S4 | Order differs after the file is reloaded (cause not yet confirmed; see RSK-01) | OPEN | Q-04 |

## 4. Actors

| ID | Actor | Description | Source label |
|---|---|---|---|
| ACT-01 | Application developer | A person who uses the tinydb Python API (`db.all()`, `db.search()`) to read documents in an ordered page. | INFERRED (S1, S2, S5: "my page"; reporter is a library user) |

## 5. Functional requirements

### FR-01: Stable order for all()
Actor: ACT-01
Statement: WHEN the application calls `Table.all()`, the system SHALL return all stored documents in insertion order (the order in which each document was first inserted), and SHALL keep the relative order of the remaining documents unchanged after an update or a removal.
Source: ASSUMED (ASM-01, ASM-02, ASM-03; basis S2, S3, S5) | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-02 P2)
Acceptance criteria:
- FR-01-AC1: a table has documents with IDs 1, 2, 3 inserted in that order, and document 1 is then updated with `update({'v': 9}, doc_ids=[1])` → `all()` returns documents with doc_id values [1, 2, 3] in that order.
- FR-01-AC2: a table has documents with IDs 1, 2, 3, and document 2 is removed with `remove(doc_ids=[2])` → `all()` returns doc_id values [1, 3].
- FR-01-AC3 (boundary): a table with 12 inserted documents → `all()` returns doc_id values [1, 2, ..., 12] in numeric order, not lexical order (1, 10, 11, 12, 2, ...).
- FR-01-AC4 (boundary): an empty table, or a table where every document has been removed → `all()` returns an empty list.
Notes: ASM-01 defines insertion order as the rule. Q-01 offers alternatives (ascending ID, last-modified order, user sort key). Q-02 decides whether an update moves a document to the end (changes FR-01-AC1). The statement that updates keep position is INFERRED from the dict-based storage model and must be confirmed by test. Related: RSK-01, RSK-02.

### FR-02: Same relative order for search()
Actor: ACT-01
Statement: WHEN the application calls `Table.search(cond)`, the system SHALL return the matching documents in the same relative order that `Table.all()` uses for the same table state, including when the result is served from the query cache.
Source: ASSUMED (ASM-04; basis S2: "`db.all()` and `db.search(...)`") | Readiness: NEEDS-CLARIFICATION (Q-01 P1)
Acceptance criteria:
- FR-02-AC1: a table has documents with IDs 1, 2, 3 and `search(where('k') == 'x')` matches documents 3 and 1 → `search` returns doc_id values [1, 3].
- FR-02-AC2: the same search is called twice with no change between calls, with an update to document 1 between them that keeps it matching → the second call returns the same order as the first call, and the order matches the relative order from `all()`.
- FR-02-AC3 (failure/boundary): a search with no matching documents → `search` returns an empty list.
Notes: Repository observation: `search()` caches results (`table.py:263-297`). The cache must not change order. Q-01 applies.

### FR-03: Order preserved across close and reopen
Actor: ACT-01
Statement: WHEN the application closes a database that uses the default JSON file storage and then reopens the same file, the system SHALL return `all()` and `search()` results in the same relative order as before the close.
Source: ASSUMED (ASM-04; basis S4: "after I close and reopen the program") | Readiness: NEEDS-CLARIFICATION (Q-01 P1, Q-04 P2)
Acceptance criteria:
- FR-03-AC1 (boundary): a JSON-backed database with 12 documents is created with default storage options, closed, and reopened from the same path → `all()` returns doc_id values [1, 2, ..., 12] in the same order as before the close.
- FR-03-AC2: a JSON-backed database has documents inserted, one updated and one removed, then is closed and reopened → `all()` after reopen returns the same doc_id sequence as `all()` immediately before close.
- FR-03-AC3 (failure): a JSON-backed database is reopened after a close with an empty file or with no table → `all()` returns an empty list.
Notes: RSK-01 describes the likely cause: `JSONStorage.write` passes `self.kwargs` to `json.dumps`, and if `sort_keys=True` is set, the document ID keys are sorted as strings, which gives "1, 10, 11, 2, ...". Whether default kwargs sort keys is OPEN (Q-04). Whether this requirement applies to custom storages is OPEN (Q-03).

## 6. Non-functional requirements

None identified. The issue states no measurable quality requirement (no speed, size or availability target). A metric would need a stakeholder answer (TBD (Q-05), P3).

## 7. Constraints

| ID | Constraint | Source label |
|---|---|---|
| None identified | The issue names no deadline, budget, platform or technology constraint. | N/A |

## 8. Dependencies

| ID | Dependency | Source label | Risk if unavailable |
|---|---|---|---|
| DEP-01 | The on-disk JSON file written by `JSONStorage`, read back on reopen | INFERRED (S4: "close and reopen") | If the file is rewritten with a different key order by an external tool, order changes without any tinydb code change. Low likelihood; unassessed. |

## 9. Risks

| ID | Risk | Cause (S# / CNF / Q) | Impact if unresolved | Proposed action |
|---|---|---|---|---|
| RSK-01 | JSON storage with `sort_keys=True` writes document ID keys in string order, so reopened results come back as 1, 10, 11, 2, ... | S4; `storages.py:147`; `tests/test_storages.py:33`; Q-04 | Order changes after reopen (the reported symptom). | Confirm default kwargs (Q-04). Add the FR-01-AC3 and FR-03-AC1 tests with default and `sort_keys=True` settings. |
| RSK-02 | Changing the order rule may break users who depend on the current order | Q-01 (order rule is not confirmed) | Behaviour change for existing callers. | Decide the rule with Q-01 and record it in the change log. Ask whether a migration note is needed (Q-07, P3). |
| RSK-03 | Ordering rule is unknown, so any implementation may not match the reporter's expectation | S1, S2, S5; Q-01 | Work done against the wrong rule. | Block implementation until Q-01 is answered. |

## 10. External evidence log

| EV | Question | URL | Accessed | Finding | Result | Affects 

</details>

<details><summary>Design (design.md)</summary>

## Approach
The stored dict already keeps insertion order in memory, so `all()` and `search()` only change order when storage reorders keys. JSON written with `sort_keys=True` (a configuration already used in `tests/test_storages.py:33`) stores ids as strings, so they reload as 1, 10, 11, 2, ... and the order cannot be recovered from the file. The fix is to make `Table` sort results by numeric document id in one shared helper, used by both `__iter__` (which backs `all()`) and `search()`. Auto-assigned ids follow insertion order, so this matches ASM-01 for the normal case. Storages, `_read_table` and `_update_table` stay unchanged. The sort is applied before the search result is cached, so cached and fresh results agree.

## Files to change
- `tinydb/table.py` :: `Table._iter_sorted_items` (new)
- `tinydb/table.py` :: `Table.__iter__`
- `tinydb/table.py` :: `Table.search`
- `tests/test_tables.py` :: `test_all_order_numeric_after_update_and_remove` (new)
- `tests/test_tables.py` :: `test_search_order_matches_all` (new)
- `tests/test_storages.py` :: `test_json_order_after_reopen_sort_keys` (new)

## Constraint check
- Rule 1 (storages subclass `Storage`): not affected, no storage class is added or changed.
- Rule 2 (`read()` returns `None` when empty, `write()` gets the full dict): not affected, `_read_table` and the write path are not touched.
- Rule 3 (middlewares): not affected, no middleware code is changed.
- Rule 4 (layering): respected, the helper lives inside `table.py` and imports nothing new; `queries.py` is not touched.
- Rule 5 (query hash identifies what it matches): respected, the query hash and `is_cacheable` are unchanged. The cache key still identifies the same matches, and the cached list is now stored in the sorted order.
- Rule 5 (all changes go through `_update_table`): respected, no write path is added. Existing `_update_table` cache clearing still applies.

## Risks
- ASSUMED interpretation (ASM-01, insertion order): the implementation orders by numeric document id. These agree for auto-assigned ids. They differ if a caller inserts with explicit ids out of order. A reviewer should reject this in the PR if insertion order must hold for explicit ids too; that would need a different on-disk format.
- Behaviour change for callers who relied on the file's key order when `sort_keys` is set, and for custom `document_id_class` values that do not convert cleanly with `int()`. The helper should fall back to the raw key in that case. Q-01 and RSK-02 remain open for this.
- Q-04 is unconfirmed: the default JSON kwargs are assumed not to sort keys. The new reopen test covers both cases so that the result does not depend on that answer.

</details>


CI for d14b909d: success (https://github.com/Aasrithakalluri/tinydb/actions/runs/44996985075)


CI for e3fa72ef: success (https://github.com/Aasrithakalluri/tinydb/actions/runs/44997211477)
