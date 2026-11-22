# `count()` without a condition

To show "N records" on my page I do `db.count(...)` and I always have to invent a condition that is always true:

```python
db.count(where('id').exists())   # not even right if docs don't have 'id'
```

`db.count()` with no arguments just raises a `TypeError`. It'd be nice if `count()` with nothing passed returned the total number of documents in the table. `count(some_query)` should keep working as today.
