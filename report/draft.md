```
>>> import readData
>>> book = readData.readBookData()
>>> print(len(book))
1190
```

```
>>> d = {'key':123}
>>> sys.getsizeof(d)
184
>>> sys.getsizeof('key')
52
>>> sys.getsizeof(123)
28
>>> sys.getsizeof({})
64
```