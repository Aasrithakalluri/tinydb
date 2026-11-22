import pytest

from tinydb import TinyDB, where
from tinydb.operations import delete, increment, decrement, add, subtract, set, multiply
from tinydb.storages import MemoryStorage


def test_delete(db):
    db.update(delete('int'), where('char') == 'a')
    assert 'int' not in db.get(where('char') == 'a')


def test_add_int(db):
    db.update(add('int', 5), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 6


def test_add_str(db):
    db.update(add('char', 'xyz'), where('char') == 'a')
    assert db.get(where('char') == 'axyz')['int'] == 1


def test_subtract(db):
    db.update(subtract('int', 5), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == -4


def test_set(db):
    db.update(set('char', 'xyz'), where('char') == 'a')
    assert db.get(where('char') == 'xyz')['int'] == 1


def test_increment(db):
    db.update(increment('int'), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 2


def test_decrement(db):
    db.update(decrement('int'), where('char') == 'a')
    assert db.get(where('char') == 'a')['int'] == 0


def test_fr_01_ac1_multiply_float_factor():
    doc = {'price': 10}
    result = multiply('price', 1.1)(doc)
    assert result is None
    assert doc['price'] == pytest.approx(11.0, abs=1e-9)


def test_fr_01_ac2_int_times_int_stays_int():
    doc = {'n': 7}
    multiply('n', 2)(doc)
    assert doc['n'] == 14
    assert isinstance(doc['n'], int)


def test_fr_01_ac3_zero_factor():
    doc = {'price': 10}
    multiply('price', 0)(doc)
    assert doc['price'] == 0


def test_fr_01_ac4_negative_factor():
    doc = {'price': 10}
    multiply('price', -1)(doc)
    assert doc['price'] == -10


def test_fr_01_ac5_identity_factor():
    doc = {'price': 10}
    multiply('price', 1)(doc)
    assert doc['price'] == 10


def test_fr_02_ac1_only_matching_documents_change():
    db_ = TinyDB(storage=MemoryStorage)
    db_.insert_multiple([
        {'category': 'books', 'price': 10},
        {'category': 'toys', 'price': 10},
    ])

    db_.update(multiply('price', 1.1), where('category') == 'books')

    books = db_.get(where('category') == 'books')
    toys = db_.get(where('category') == 'toys')
    assert books['price'] == pytest.approx(11.0, abs=1e-9)
    assert toys['price'] == 10


def test_fr_02_ac2_empty_match_changes_nothing():
    db_ = TinyDB(storage=MemoryStorage)
    db_.insert_multiple([
        {'category': 'books', 'price': 10},
        {'category': 'toys', 'price': 20},
    ])

    db_.update(multiply('price', 1.1), where('category') == 'games')

    assert [d['price'] for d in db_.all()] == [10, 20]


def test_fr_02_ac3_multiple_matches_all_updated():
    db_ = TinyDB(storage=MemoryStorage)
    db_.insert_multiple([
        {'category': 'books', 'price': 10},
        {'category': 'books', 'price': 20},
    ])

    db_.update(multiply('price', 2), where('category') == 'books')

    assert sorted(d['price'] for d in db_.all()) == [20, 40]


def test_fr_03_ac1_missing_field_raises_key_error():
    doc = {'name': 'x'}
    with pytest.raises(KeyError):
        multiply('price', 1.1)(doc)
    assert doc == {'name': 'x'}


def test_fr_03_ac2_string_value_raises_type_error():
    doc = {'price': '10'}
    with pytest.raises(TypeError):
        multiply('price', 1.1)(doc)
    assert doc['price'] == '10'


def test_fr_03_ac3_string_factor_raises_type_error():
    with pytest.raises(TypeError):
        multiply('price', '1.1')


def test_fr_03_ac4_bool_value_raises_type_error():
    doc = {'flag': True}
    with pytest.raises(TypeError):
        multiply('flag', 2)(doc)
    assert doc['flag'] is True
