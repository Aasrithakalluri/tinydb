from tinydb import TinyDB, where, Query
from tinydb.storages import MemoryStorage

def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'a', 'nickname': 'bob'})
    db.insert({'name': 'b', 'nickname': 'al'})
    db.insert({'name': 'c'})
    return db

def test_ne_includes_docs_without_field():
    names = sorted(d['name'] for d in _db().search(where('nickname') != 'bob'))
    assert names == ['b', 'c']

def test_ne_equals_negated_eq():
    db = _db()
    assert db.search(where('nickname') != 'bob') == db.search(~(where('nickname') == 'bob'))

def test_ne_still_excludes_equal_and_nested_missing():
    db = _db()
    assert all(d.get('nickname') != 'bob' for d in db.search(Query().nickname != 'bob'))
    assert len(db.search(where('profile').city != 'x')) == 3
