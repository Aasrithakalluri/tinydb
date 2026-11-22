from tinydb import TinyDB, where
from tinydb.table import Document
from tinydb.storages import MemoryStorage

def _populate(db):
    db.insert({'n': 'a'})
    db.insert(Document({'n': 'z'}, doc_id=10))
    db.insert(Document({'n': 'c'}, doc_id=5))

def ids(docs): return [d.doc_id for d in docs]

def test_all_and_search_sorted_by_doc_id_memory():
    db = TinyDB(storage=MemoryStorage); _populate(db)
    assert ids(db.all()) == [1, 5, 10]
    assert ids(db.search(where('n').exists())) == [1, 5, 10]

def test_order_consistent_after_reload(tmp_path):
    p = str(tmp_path / 'a.json')
    db = TinyDB(p); _populate(db); before = ids(db.all()); db.close()
    after = ids(TinyDB(p).all())
    assert before == after == [1, 5, 10]

def test_extra_update_returns_ids_ascending_and_iter_matches():
    db = TinyDB(storage=MemoryStorage); db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])
    assert db.update({'a': 9}, doc_ids=[3, 1, 2]) == [1, 2, 3]
    assert ids(list(db)) == [1, 2, 3]


# --- added 2026-11-22 after the maintainer answered the pipeline's questions (1a ascending id, 2a keep position, 3a built-in storages)
def test_updated_document_keeps_its_position_memory():
    db = TinyDB(storage=MemoryStorage); db.insert_multiple([{'n': 'a'}, {'n': 'b'}, {'n': 'c'}])
    db.update({'n': 'B2'}, where('n') == 'b')
    assert ids(db.all()) == [1, 2, 3] and ids(db.search(where('n').exists())) == [1, 2, 3]
    db.update({'n': 'A2'}, where('n') == 'a')
    assert ids(db.all()) == [1, 2, 3]

def test_updated_document_keeps_its_position_after_reopen(tmp_path):
    p = str(tmp_path / 'b.json')
    db = TinyDB(p); db.insert_multiple([{'n': i} for i in range(12)])
    db.update({'n': 99}, doc_ids=[2]); db.remove(doc_ids=[5]); db.insert({'n': 'new'}); db.close()
    assert ids(TinyDB(p).all()) == sorted(ids(TinyDB(p).all())) == [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13]

def test_numeric_not_lexical_order_with_sorted_keys_storage(tmp_path):
    from tinydb.storages import JSONStorage
    p = str(tmp_path / 'c.json')
    db = TinyDB(p, sort_keys=True); db.insert_multiple([{'n': i} for i in range(12)]); db.close()
    assert ids(TinyDB(p, sort_keys=True).all()) == list(range(1, 13))
