# Modifying a document I got from `search()` changes what later searches return

I loaded some documents with `search()`, tweaked the dicts in Python to show something in my UI (I never called `update()`), and later the same query returned my tweaked values instead of what is actually stored in the file.

```python
db = TinyDB('db.json')
db.insert({'name': 'a', 'tags': ['x']})
q = where('name') == 'a'

rows = db.search(q)
rows[0]['name'] = 'CHANGED'
rows[0]['tags'].append('oops')

print(db.search(q))
# [{'name': 'CHANGED', 'tags': ['x', 'oops']}]   <- file on disk still says 'a' / ['x']
```

If I restart the program I get the correct data back, so the file is fine, but within one process the result of the second search is wrong. I'd expect searching the same query twice to return the stored data both times, no matter what I did to the previous result.
