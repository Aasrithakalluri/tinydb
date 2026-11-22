import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

def test_multiply_ints_and_floats():
    from tinydb.operations import multiply
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 2.5, 'c': 'books'}])
    db.update(multiply('p', 2), where('c') == 'books')
    assert sorted(d['p'] for d in db.all()) == [5.0, 20]

def test_multiply_only_matching_docs():
    from tinydb.operations import multiply
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 10, 'c': 'toys'}])
    db.update(multiply('p', 3), where('c') == 'books')
    assert db.get(where('c') == 'toys')['p'] == 10
    assert db.get(where('c') == 'books')['p'] == 30

def test_multiply_missing_field_raises_like_add():
    from tinydb.operations import multiply, add
    db = TinyDB(storage=MemoryStorage)
    db.insert({'x': 1})
    with pytest.raises(KeyError):
        db.update(add('p', 1))
    with pytest.raises(KeyError):
        db.update(multiply('p', 2))

def test_multiply_by_zero_and_negative():
    from tinydb.operations import multiply
    db = TinyDB(storage=MemoryStorage); db.insert({'p': 4})
    db.update(multiply('p', 0)); assert db.all()[0]['p'] == 0
    db.update(multiply('p', -1)); assert db.all()[0]['p'] == 0
