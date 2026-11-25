from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def test_fr_01_ac1_table_without_documents():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('items')

    assert table.is_empty() is True


def test_fr_01_ac2_table_with_one_document():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('items')
    table.insert({'a': 1})

    assert table.is_empty() is False


def test_fr_01_ac3_table_after_removing_only_document():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('items')
    doc_id = table.insert({'a': 1})
    table.remove(doc_ids=[doc_id])

    assert table.is_empty() is True


def test_fr_01_ac4_table_after_remove_and_insert():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('items')
    doc_id = table.insert({'a': 1})
    table.remove(doc_ids=[doc_id])
    table.insert({'b': 2})

    assert table.is_empty() is False


def test_fr_01_ac5_table_returns_bool_type():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('items')

    result = table.is_empty()

    assert type(result) is bool
    assert result is True


def test_fr_02_ac1_default_table_with_two_documents():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1})
    db.insert({'a': 2})

    assert db.is_empty() is False


def test_fr_02_ac2_new_database_without_documents():
    db = TinyDB(storage=MemoryStorage)

    assert db.is_empty() is True


def test_fr_02_ac3_default_table_only_document_removed():
    db = TinyDB(storage=MemoryStorage)
    doc_id = db.insert({'a': 1})
    db.remove(doc_ids=[doc_id])

    assert db.is_empty() is True


def test_fr_02_ac4_documents_only_in_named_table():
    db = TinyDB(storage=MemoryStorage)
    db.table('users').insert({'name': 'alice'})

    assert db.is_empty() is True


def test_fr_02_ac5_new_database_returns_bool_type():
    db = TinyDB(storage=MemoryStorage)

    result = db.is_empty()

    assert type(result) is bool
    assert result is True


def test_fr_03_ac1_named_table_with_two_documents():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'alice'})
    users.insert({'name': 'bob'})

    assert db.table('users').is_empty() is False


def test_fr_03_ac2_named_table_all_documents_removed():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    ids = users.insert_multiple([{'name': 'alice'}, {'name': 'bob'}])
    users.remove(doc_ids=ids)

    assert db.table('users').is_empty() is True


def test_fr_03_ac3_empty_table_while_other_table_has_document():
    db = TinyDB(storage=MemoryStorage)
    db.table('users').insert({'name': 'alice'})
    db.table('users').remove(doc_ids=[1])
    db.table('posts').insert({'title': 'hello'})

    assert db.table('users').is_empty() is True


def test_fr_03_ac4_never_written_table():
    db = TinyDB(storage=MemoryStorage)
    db.table('users').insert({'name': 'alice'})

    assert db.table('archive').is_empty() is True
