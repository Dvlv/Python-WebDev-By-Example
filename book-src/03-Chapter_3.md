# Chapter 3
## Testing with Pytest
Automated tests allow us to ensure that our site's expected functionality will stay the same as we continue adding features. This prevents us from having to manually use each aspect of our site every time we make changes.

If you’d like a detailed look into Pytest before diving in, check out [Appendix 2](#appendix-2---pytest).

To get started with Pytest, create a folder in the root directory of your project named `tests` and inside create a file named `helpers.py`.

```python
from models.product import Product

__all__ = ["create_test_product"]


def create_test_product(name: str, price: str):
    p = Product()
    p.name = name
    p.price = price
    p.save()

    return p
```

All helper functions for our tests will be stored in this file. This avoids having to either re-define them in multiple tests, or elongate each test function by creating models manually.

We start off with just one function - `create_test_product` - which will create a record in our Product database table with the supplied name and price. Creating a record in Peewee can be done by creating an instance of a model class. You can then assign values to each of the defined class attributes representing the data to be stored for each column. Once the necessary fields are populated, the `save` method will write this new row to the database.

We also define an `__all__` variable, which is a special python variable to allow a cleaner use of `import *` statements. When a file uses `from tests.helpers import *` it will normally import all definitions contained in that file. This means it would import the `Product` class in this file's current state. However, when we define `__all__` only the definitions inside this list will be imported. This means, in the file's current state, any test using `from tests.helpers import *` will _only_ be importing our `create_test_product` function, and _not_ the `Product` class.

With this database helper function in place, we now need the ability to switch our Flask server into test mode. Create another file in the `tests` folder, this time named `__init__.py`:

```python
from web_server import app

app.config.update(
    {
        "TESTING": True,
    }
)

testing_app = app.test_client()
```

This file will create a new variable called `testing_app` which is just our Flask server in testing mode. We can now use methods such as `get` and `post` to issue requests to our server inside tests.

Let's now create our first test. We will load up the index page of the site and check each product is displayed.

Create a file named `test_products.py` in your `tests` folder:

```python
from tests import testing_app
from tests.helpers import *


def test_index_displays_product_names():
    create_test_product("Toothbrush", "2.00")
    create_test_product("Toothpaste", "1.00")

    res = testing_app.get("/")

    assert res.status_code == 200
    
    res_data = res.get_data().decode("utf-8")
    
    assert "Toothbrush" in res_data
    assert "Toothpaste" in res_data
```

We grab our `testing_app` server and use a star-import to pull in our `create_test_product` helper. 

The `test_index_displays_product_names` function begins by creating two products in our database, then uses `testing_app` to issue a request to the index page of our site. We then use an `assert` statement to ensure that the HTTP status code of the response was 200 Successful. 

Once we know the request was successful, we then get the HTML returned by the endpoint using `res.get_data()` and decode it into a UTF-8 string. We can then test that this string contains the names of our two test products.

We are now ready to run this test - but wait! Our database models are still pointing to our main database, which could be our production database. Obviously we need an ephemeral copy which can be populated and checked-against for each test, and then cleared away ready for the next. This both prevents data from ending up in our real database, and allows unit tests to run without needing to keep track of which previous tests may have added or removed records.

There are multiple ways to solve this problem, but the way I find easiest is to use a decorator above each test which passes in only the tables required for this particular test to run. 

Head back to `tests/helpers.py` and add in the following:

```python
from functools import wraps
from playhouse.sqlite_ext import SqliteExtDatabase
...

__all__ = ["create_test_product", "with_test_db"]

def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = SqliteExtDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator
    
...
```

This function takes a `tuple` of Peewee models, creates a new, in-memory Sqlite database and binds it to the provided models. It then runs the decorated function, drops all tables in the database, and closes the connection.

Head back to `test_products.py` and wrap our test with the new decorator:

```python
from models.product import Product
...

@with_test_db((Product,))
def test_index_displays_product_names():
    ...
```
Note the trailing comma inside our tuple. Without this, python will interpret our `Product` model as a single independent argument, rather than as part of a one-item tuple.

_Now_ we are finally ready to run our test. Open up a command line at the root of your project and run the `pytest` command. Hopefully you should see a success message saying `1 passed` in green.

If you see an error about packages not being found, you may need to adjust the `PYTHONPATH` environment variable. In Linux or MacOS running bash or zsh, this should be done like so:

```bash
export PYTHONPATH=.

pytest
```

Congratulations, you have now written your first test for this project! Let's not get ahead of ourselves though, there's still another page to test. Let's add more tests to `test_products`:

```python
@with_test_db((Product,))
def test_view_product_shows_product_name_and_price():
    create_test_product("Toothbrush", "2.00")

    res = testing_app.get("/Toothbrush")

    assert res.status_code == 200

    res_data = res.get_data().decode("utf-8")
    
    assert "Toothbrush" in res_data
    assert "£2.00" in res_data


@with_test_db((Product,))
def test_view_product_shows_404_if_not_found():
    create_test_product("Toothbrush", "2.00")

    res = testing_app.get("/Bananas")

    assert res.status_code == 404
```

These new tests will both load the `view_product` route. The first will load a valid product and check the name and price are displayed on the page. The second loads a non-existent product and asserts that the HTTP response is a 404.

Head back to your command line and run your tests again with `pytest`. You should now see `3 passed` in green. 

Great, now we can assure that our site's basic functionality is in place just by running the `pytest` command at any time. Let's now progress the abilities of our site by adding a separate section for admininstrators, where they can enter details of new products without writing SQL migrations.
