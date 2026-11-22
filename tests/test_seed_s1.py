from tinydb import Query, where


def test_ne_matches_document_without_field():
    assert (Query().nickname != 'bob')({'name': 'c'})
    assert (Query().nickname != 'bob')({'nickname': 'al'})
    assert not (Query().nickname != 'bob')({'nickname': 'bob'})


def test_ne_is_negation_of_eq_top_level():
    doc = {'name': 'c'}
    assert (Query().nickname != 'bob')(doc) == (~(Query().nickname == 'bob'))(doc)
