from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def test_update_returns_ids_ascending():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])
    assert db.update({'a': 9}, doc_ids=[3, 1, 2]) == [1, 2, 3]
