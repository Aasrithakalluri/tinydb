# `!=` skips documents that don't have the field, but `~(... == ...)` doesn't

I have a table of users where some records have no `nickname` at all. I wanted everyone whose nickname is not "bob":

```python
db.search(where('nickname') != 'bob')
```

This only returns the users that *have* a nickname other than bob. Users without a `nickname` are silently left out. But when I write the same thing with `~`:

```python
db.search(~(where('nickname') == 'bob'))
```

I get the users without a nickname too. Same logical question, two different answers, which cost me an afternoon because I assumed they were equivalent.

I'd expect `!=` to behave like the negation of `==`: a document that has no such field is "not equal to bob", so it should be returned.

```python
db.insert({'name': 'a', 'nickname': 'bob'})
db.insert({'name': 'b', 'nickname': 'al'})
db.insert({'name': 'c'})
db.search(where('nickname') != 'bob')   # I get only b, expected b and c
```
