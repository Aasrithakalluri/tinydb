"""
A collection of update operations for TinyDB.

They are used for updates like this:

>>> db.update(delete('foo'), where('foo') == 2)

This would delete the ``foo`` field from all documents where ``foo`` equals 2.
"""


from collections.abc import Callable, MutableMapping
from typing import Any, Union


def delete(field: str) -> Callable[[MutableMapping], None]:
    """
    Delete a given field from the document.
    """
    def transform(doc: MutableMapping):
        del doc[field]

    return transform


def add(field: str, n: Union[int, float, str]) -> Callable[[MutableMapping], None]:
    """
    Add ``n`` to a given field in the document.

    Also works for strings (concatenation), matching the documented behavior.
    """
    def transform(doc: MutableMapping):
        doc[field] += n

    return transform


def subtract(field: str, n: Union[int, float]) -> Callable[[MutableMapping], None]:
    """
    Subtract ``n`` to a given field in the document.
    """
    def transform(doc: MutableMapping):
        doc[field] -= n

    return transform


def multiply(field: str, factor: Union[int, float]) -> Callable[[MutableMapping], None]:
    """
    Multiply a given field in the document by ``factor``.

    Only int and float values are supported. Booleans are rejected even though
    they are a subclass of int. The factor is validated when this function is
    called, not when the transform is applied.
    """
    if isinstance(factor, bool) or not isinstance(factor, (int, float)):
        raise TypeError(f"factor must be int or float, not {type(factor).__name__}")

    def transform(doc: MutableMapping):
        if field not in doc:
            return
        value = doc[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"field {field!r} must be int or float, not {type(value).__name__}"
            )
        doc[field] = value * factor

    return transform


def set(field: str, val: Any) -> Callable[[MutableMapping], None]:
    """
    Set a given field to ``val``.
    """
    def transform(doc: MutableMapping):
        doc[field] = val

    return transform


def increment(field: str) -> Callable[[MutableMapping], None]:
    """
    Increment a given field in the document by 1.
    """
    def transform(doc: MutableMapping):
        doc[field] += 1

    return transform


def decrement(field: str) -> Callable[[MutableMapping], None]:
    """
    Decrement a given field in the document by 1.
    """
    def transform(doc: MutableMapping):
        doc[field] -= 1

    return transform
