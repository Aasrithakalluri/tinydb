# [AutoSE] Modifying a document I got from `search()` changes what later searches return

https://github.com/Aasrithakalluri/tinydb/pull/14

Closes #2

Automated by AutoSE (Planner/Builder: Haiku, Reviewer: Sonnet). A human decides whether to merge.

Artifacts are attached to the workflow run: https://github.com/Aasrithakalluri/tinydb/actions/runs/44996288135

## Acceptance criteria
- FR-01-AC1: table holds `{'name': 'a', 'tags': ['x']}`; `rows = db.search(q)` with `q = where('name') == 'a'`; `rows[0]['name'] = 'CHANGED'` → second `db.search(q)` returns `[{'name': 'a', 'tags': ['x']}]`.
- FR-01-AC2: same table; `rows[0]['tags'].append('oops')` → second `db.search(q)` returns a document whose `tags` equals `['x']`.
- FR-02-AC1: `db.search(q)` returns 1 document; `db.insert({'name': 'a', 'tags': []})` → next `db.search(q)` returns 2 documents.


CI for 6accc9e5: success (https://github.com/Aasrithakalluri/tinydb/actions/runs/44996449077)
