from tinydb import TinyDB, where
from tinydb.operations import multiply
from tinydb.storages import MemoryStorage


def test_multiply_scales_matching_documents():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 10, 'c': 'books'}, {'p': 10, 'c': 'toys'}])
    db.update(multiply('p', 3), where('c') == 'books')
    assert db.get(where('c') == 'books')['p'] == 30
    assert db.get(where('c') == 'toys')['p'] == 10


def test_multiply_float_factor():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'p': 10})
    db.update(multiply('p', 1.5))
    assert db.all()[0]['p'] == 15.0
