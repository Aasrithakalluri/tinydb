# Add `is_empty()` to tables

Checking whether a table has any documents currently needs `len(db) == 0`, which reads badly in conditions. A method `db.is_empty()` returning `True` when the table has no documents and `False` otherwise would be nicer. It should also work on named tables: `db.table('users').is_empty()`.
