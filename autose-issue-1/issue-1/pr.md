# [AutoSE] `!=` skips documents that don't have the field, but `~(... == ...)` doesn't

https://github.com/Aasrithakalluri/tinydb/pull/15

Closes #1

Automated by AutoSE (Planner/Builder: Haiku, Reviewer: Sonnet). A human decides whether to merge.

Artifacts are attached to the workflow run: https://github.com/Aasrithakalluri/tinydb/actions/runs/44996285044

## Acceptance criteria
- FR-01-AC1: query `where('nickname') != 'bob'` evaluated on `{'name': 'c'}` → returns True.
- FR-01-AC2: query `where('nickname') != 'bob'` evaluated on `{}` (boundary: empty document) → returns True.
- FR-01-AC3: after inserting `{'name': 'a', 'nickname': 'bob'}`, `{'name': 'b', 'nickname': 'al'}` and `{'name': 'c'}`, `db.search(where('nickname') != 'bob')` → returns the documents named 'b' and 'c' and not 'a' (order not checked).
- FR-01-AC4: for each of the three documents in FR-01-AC3, `(where('nickname') != 'bob')(doc)` equals `(~(where('nickname') == 'bob'))(doc)` → the two results are equal for all three documents.
- FR-02-AC1: document `{'nickname': 'bob'}` with query `where('nickname') != 'bob'` → returns False.
- FR-02-AC2: document `{'nickname': 'al'}` with query `where('nickname') != 'bob'` → returns True.
- FR-02-AC3: document `{'nickname': None}` with query `where('nickname') != 'bob'` (boundary: present field with `None` value, ASM-03) → returns True.
- FR-02-AC4: document `{'nickname': ['bob']}` with query `where('nickname') != ['bob']` (boundary: list value) → returns False.
- FR-03-AC1: document `{'profile': {}}` with query `where('profile').nickname != 'bob'` → returns True.
- FR-03-AC2: document `{}` with query `where('profile').nickname != 'bob'` (boundary: parent key absent) → returns True.
- FR-03-AC3: document `{'profile': 5}` with query `where('profile').nickname != 'bob'` (failure case: parent is not a mapping) → returns True without raising an exception.
- FR-03-AC4: document `{'profile': {'nickname': 'bob'}}` with query `where('profile').nickname != 'bob'` → returns False.


CI for 5cf6c8fc: success (https://github.com/Aasrithakalluri/tinydb/actions/runs/44996462096)
