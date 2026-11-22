from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def test_count_without_condition():
    db = TinyDB(storage=MemoryStorage)
    assert db.count() == 0
    db.insert_multiple([{'a': 1}, {'a': 2}, {}])
    assert db.count() == 3
    assert db.count(where('a') == 1) == 1
