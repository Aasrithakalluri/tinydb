from tinydb import TinyDB, where

def _db(tmp_path):
    db = TinyDB(str(tmp_path / 'db.json'))
    db.insert({'name': 'a', 'tags': ['x']})
    return db

def test_scalar_mutation_does_not_leak(tmp_path):
    db = _db(tmp_path); q = where('name') == 'a'
    db.search(q)[0]['name'] = 'CHANGED'
    assert db.search(q) == [{'name': 'a', 'tags': ['x']}]

def test_nested_mutation_does_not_leak(tmp_path):
    db = _db(tmp_path); q = where('name') == 'a'
    db.search(q)[0]['tags'].append('oops')
    assert db.search(q)[0]['tags'] == ['x']

def test_get_and_cache_still_correct_after_write(tmp_path):
    db = _db(tmp_path); q = where('name') == 'a'
    db.get(q)['name'] = 'zzz'
    assert db.get(q)['name'] == 'a'
    db.update({'name': 'b'}, q)
    assert db.search(where('name') == 'b') and not db.search(q)
