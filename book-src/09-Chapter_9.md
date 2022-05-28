# Appendix 2 - Pytest

[(Back to Chapter 3)](#chapter-3)

In these appendices I will be covering some more complex parts of the mentioned libraries which I couldn't fit into our simple example, but still deem important to know. These can be read either before following the book's examples, or after finishing the project.

As always, the official Pytest docs are going to be more accurate than what is written here.

These examples are correct for Pytest version **7.0.0**.

## Basics

Tests by default live in a folder called `tests`. Within that folder, any python files which begin with `test_` will be run by Pytest. Similarly, any functions inside those files which begin with `test_` will be detected and executed as tests.

Running tests is achieved by executing the command `pytest` in the same directory as your `tests` folder. If you specify a file as the second argument, e.g. `pytest tests/models/test_models.py`, only that file will be run.

Some of the flags you may want to pass to the command are:

- `-s`  Show the ouput of `print` statements.
- `-x`   Stop after a test fails.
- `-v`  Display the file and function of each test as it runs.
- `-k` Only run tests whose name matches a provided string. For example `pytest -k email` will only run tests if their function name contains the word "email".

You can pass multiple flags in one go, for example `pytest -sxv`.


## Advanced

### Fixtures
Fixtures are a rather deep topic, which you can find on the Pytest docs in more detail than I could ever write. However, for the purpose of understanding this book, you can think of a fixture as _an object injected into a test which requires it_.

The two fixtures I find myself using the most are `mocker` for Mocking and `monkeypatch` for Patching. 

### Mocking

Mocking is replacing a piece of code with a dummy object which keeps track of how many times it was called and with what arguments. This dummy function will _not_ execute the original code.

Mocking in Pytest is made very easy with the `pytest-mock` library. With this installed simply add a parameter named `mocker` to your test functions and a `Mock` object will be injected.

#### Mocking a Function 
To mock a function, pass a string representing the import path to the function to `mocker.patch`, like so:

```python
mocker.patch("helpers.emails.send_email")
```

Now in your test, import this function and use a method to check it was / wasn't called:

```python
def test_send_email_called(mocker):
    mocker.patch("helpers.emails.send_email")
    
    function_which_should_send_email()
    
    from helpers.emails import send_email
    
    send_email.assert_called_once()
```

#### Mocking an Object
To mock a method of an object, rather than a standalone function, use `mocker.patch.object`. Pass the object as the first argument, and a string of the method to mock as the second.

```python
mocker.patch.object(Book, "get_total_revenue")
```

You can now check the method was called in much the same way as a function:

```python
def test_get_total_revenue(mocker):
    from models.book import Book
    
    mocker.patch.object(Book, "get_total_revenue")
    
    get_all_book_revenues()
        
    Book.get_total_revenue.assert_called_once()
```

### Spying
Spying is like Mocking, except the original functionality of the mocked function _will_ execute. This is useful during integration tests, where subsequent function calls rely on the results of the one you wish to mock.

Spying is also handled by the `pytest-mock` module, and is available in the `mocker` fixture.

```python
def test_get_total_revenue(mocker):
    from models.book import Book
    
    book_spy = mocker.spy(Book, "get_total_revenue")
    
    get_all_book_revenues()
        
    book_spy.assert_called_once()
```

### Patching

Patching is changing the behaviour of a function or method temporarily for the duration of a single test. This is useful for integration tests which rely on functions gathering data which is not static, such as the current date or a request to an external API.

Patching is achieved using the `monkeypatch` fixture built in to Pytest. 

#### Patching a function

Patching a function is a bit more complicated than mocking, but the syntax is generally similar. The `monkeypatch` object uses the `setattr` method to patch a function, which requires the function-to-patch as the first argument, and the replacement function as the second.

Instead of passing the function directly, however, you need to pass its `__code__` attribute:

```python
def patched_send_email():
    print("sending")
    
monkeypatch.setattr("helpers.emails.send_email.__code__", patched_send_email.__code__)
```

#### Patching an Object

Patching an object does not require the use of `__code__`, and is also achieved via `setattr`. The first argument is the object, the second is a string of the method to patch, and the third is the replacement function:

```python
from models.book import Book

def patched_get_total_rev():
    return 50.00

monkeypatch.setattr(Book, "get_total_revenue", patched_get_total_rev)
```















