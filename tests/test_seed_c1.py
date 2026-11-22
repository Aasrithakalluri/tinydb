from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def test_count_without_condition():
    db = TinyDB(storage=MemoryStorage)
    assert db.count() == 0
    db.insert_multiple([{'a': 1}, {'a': 2}, {}])
    assert db.count() == 3


def test_count_is_per_table():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1})
    other = db.table('other')
    other.insert_multiple([{'a': 1}, {'a': 2}])
    assert db.count() == 1 and other.count() == 2
