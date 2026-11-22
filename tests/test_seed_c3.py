from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage


def test_ne_matches_document_without_field():
    assert (Query().nickname != 'bob')({'name': 'c'})
    assert not (Query().nickname != 'bob')({'nickname': 'bob'})


def test_ne_and_eq_do_not_share_cached_results():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'n': 1}, {'n': 2}])
    assert len(db.search(Query().n == 1)) == 1
    assert len(db.search(Query().n != 1)) == 1
