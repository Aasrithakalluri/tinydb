The PR adds `multiply(field, factor)` and it works for the issue's example. I found no defect I could reproduce.

- **Expected behaviour:** `multiply('price', 1.1)` should work with `db.update` and scale only the matching documents. It should follow the style of the other operations.
- **Architecture:** In `tinydb/operations.py`, `multiply` is a pure transform and adds no imports, which fits the "operations import nothing from the package" rule. Constraint 4 (layering) is respected. Constraint 5 (writes go through `_update_table`) also holds, because `multiply` only mutates the document passed to it and `Table.update` does the writing. Constraints 1–3 (storages and middlewares) are not touched.
- **Test suite:** `python -m pytest -q` gave 245 passed.
- **Experiments:** I ran a `python -c` script against `MemoryStorage`.
  - **Issue example:** after `update(multiply('price', 1.1), where('category') == 'books')`, `price` changed from 10 to 11.0.
  - **Cached query:** the same query repeated after the write returned the new price, so the cache was cleared.
  - **Missing field:** a document without `price` raised `KeyError('price')`.
  - **Empty table:** updating an empty table returned `[]` without error.

**Notes:**
- When `update` hits a missing field partway through, documents already processed stay changed. In my run the first matching document was already 22.0 after the `KeyError`, and `MemoryStorage` keeps the same objects. I did not check whether `add` and the other operations behave the same way. I treat it as existing `Table.update` behaviour, not something this PR introduced.
- `multiply` rejects `bool`, `Decimal` and `Fraction`. That is stricter than the other operations, but it is documented and tested.

```json
{"verdict":"approve","issue_type":"none","tests_run":true,"findings":[],"notes":["Full suite: 245 passed.","Issue example, cached-query repeat after write, missing field (KeyError) and empty table all behave correctly.","Update is not atomic if a later matching doc lacks the field with MemoryStorage (earlier docs stay changed); I did not check whether the other operations behave the same way.","Decimal/Fraction values or factors are rejected; stricter than the other operations, but documented and tested."]}
```