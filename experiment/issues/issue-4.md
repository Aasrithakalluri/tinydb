# Add a `multiply` update operation

There are `add`, `subtract`, `increment`, `decrement` in `tinydb.operations` but nothing to scale a number. I need to apply a price change (e.g. everything x1.1) and currently have to write my own lambda each time.

Would be great to have:

```python
from tinydb.operations import multiply
db.update(multiply('price', 1.1), where('category') == 'books')
```

Same style as the other operations (takes the field name and the factor).
