from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def test_cached_search_returns_independent_copies():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'a', 'tags': ['x']})
    q = where('name') == 'a'
    db.search(q)
    second = db.search(q)
    second[0]['tags'].append('oops')
    assert db.search(q)[0]['tags'] == ['x']
