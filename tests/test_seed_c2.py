import pytest
from tinydb import TinyDB, where
from tinydb.operations import multiply
from tinydb.storages import MemoryStorage


def test_multiply_scales_matching_documents():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 10, 'c': 'toys'}])
    db.update(multiply('p', 3), where('c') == 'books')
    assert db.get(where('c') == 'books')['p'] == 30
    assert db.get(where('c') == 'toys')['p'] == 10


def test_multiply_missing_field_raises_like_add():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'x': 1})
    with pytest.raises(KeyError):
        db.update(multiply('p', 2))
