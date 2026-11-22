from tinydb import TinyDB, where
from tinydb.table import Document
from tinydb.storages import MemoryStorage


def test_results_are_ordered_by_document_id():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'n': 'a'})
    db.insert(Document({'n': 'z'}, doc_id=5))
    db.insert(Document({'n': 'c'}, doc_id=3))
    assert [d.doc_id for d in db.all()] == [1, 3, 5]
    assert [d.doc_id for d in db.search(where('n').exists())] == [1, 3, 5]
