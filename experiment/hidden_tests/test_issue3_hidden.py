from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

def test_count_empty_is_zero():
    assert TinyDB(storage=MemoryStorage).count() == 0

def test_count_all_after_inserts_and_removes():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'b': 2}, {}])
    assert db.count() == 3
    db.remove(where('a') == 1)
    assert db.count() == 2

def test_count_with_cond_and_on_named_table():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'a': 2}])
    t = db.table('other'); t.insert({'a': 1})
    assert db.count(where('a') == 1) == 1
    assert t.count() == 1 and db.count() == 2
