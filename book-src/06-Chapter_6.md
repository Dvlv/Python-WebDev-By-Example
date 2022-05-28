# Chapter 6
## More Testing

Now that our admin and site are fully-functional, we should add some automated tests to ensure that our site's core functionality will still work as we add features in the future. 

We'll start with our admin section, since we need to ensure it's only available when a user is logged in.

### Testing the Admin

As we have two distinct parts to our site, we should split our test suite up to match. Create two folders in your `tests` folder - `site` and `admin`. Then move your `test_index.py` file into `site` and rename it to `test_site.py`. Now create a `test_admin.py` file inside your `tests/admin` folder and add the following:

```python
from models.admin_user import AdminUser
from models.product import Product
from tests.helpers import *
from tests import testing_app

def test_index_redirects_to_login_if_not_logged_in():
    res = testing_app.get("/admin/")

    assert res.status_code == 302
    assert b"/login" in res.get_data()
```

This first test tries to load the `/admin` page and asserts that the response is a 302 (redirect). We also see the URL we are being sent to, and we assert that it is the `/login` page. You will notice the `b` in front of our `"/login"` string - this is because HTTP responses are bytes. You can check a response's content with either a bytes string (like above) or by adding `.decode("utf-8")` to `res.get_data()` (as we did in chapter 3). We'll be using bytes strings in this chapter, as it's shorter to write.

```python
def test_index_does_not_redirect_if_logged_in():
    with testing_app.session_transaction() as s:
        s.clear()
        s["logged_in"] = True
        s["admin_user_id"] = 1

    res = testing_app.get("/admin/")

    assert res.status_code == 200
```

This test uses the `session_transaction` method to let us modify the Flask session before our request. We use this to set the `"logged_in"` and `"admin_user_id"` values so that we are now logged in as an admin. We once again load the `/admin` route and assert that it is successful (rather than a redirect). 

Logging in with the `session_transaction` method will be needed for a lot of our methods, so let's create a helper at the top of this file to perform this.

```python
def admin_login():
    with testing_app.session_transaction() as s:
        s.clear()
        s["logged_in"] = True
        s["admin_user_id"] = 1
```

Before we use this, however, we should assure our login functionality works as intended:

```python
from models.admin_user import AdminUser
...

@with_test_db((AdminUser,))
def test_login_logs_user_in_with_correct_details():
    with testing_app.session_transaction() as s:
        s.clear()

    create_test_admin_user("admin", "admin")

    form_data = {"username": "admin", "password": "admin"}

    res = testing_app.post("/admin/login", data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert b"Welcome to the admin" in res.get_data()


@with_test_db((AdminUser,))
def test_login_shows_error_with_incorrect_details():
    with testing_app.session_transaction() as s:
        s.clear()

    create_test_admin_user("admin", "admin")

    form_data = {"username": "admin", "password": "password"}

    res = testing_app.post("/admin/login", data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert b"Please try again!" in res.get_data()
```

Before testing our login system we need to ensure there is no session, so we use `session_transaction` to ensure the session has been cleared. We then need to make an `AdminUser` which can be authenticated against. In the first test, we create our form data with the correct login details and use the `testing_app.post` method to send this to the login URL. The `data` argument is used to send our `form_data` as POST data, and the `follow_redirects` argument will make the `res` response contain the page we are redirected to, rather than a 302 status code. We then check the page we are taken to and `assert` that it contains the text from our admin header.

On the second test, since we send the wrong details, we check that the response contains our `flash`ed error message.

Before we can run these first few tests we'll need that helper function to create an `AdminUser`. Open up `tests/helpers.py` and we'll add helpers for our other models:

```python
from datetime import datetime
from models.admin_user import AdminUser
from models.order import Order
...

def create_test_admin_user(username: str, password: str):
    from werkzeug.security import generate_password_hash

    u = AdminUser()
    u.username = username
    u.password = generate_password_hash(password)
    u.save()

    return u


def create_test_order(email: str, products: dict):
    o = Order()
    o.email = email
    o.timestamp_created = datetime.now().format("%Y-%m-%d %H:%M:%S")
    o.products = products
    o.save()

    return o
```

Now we have the ability to make `AdminUser` and `Order` instances easily. Back to `tests/admin/test_admin.py`, let's write tests for the CRUD functionality for `Product`s.

```python
@with_test_db((Product,))
def test_create_product_shows_form():
    admin_login()

    res = testing_app.get(f"/admin/create-product")
    res_data = res.get_data()

    assert b'<form name="product_form"' in res_data


@with_test_db((Product,))
def test_edit_product_shows_populated_form():
    admin_login()

    p = create_test_product("Floss", "1.50")

    res = testing_app.get(f"/admin/{p.id}")
    res_data = res.get_data()

    assert b"Floss" in res_data
    assert b"1.50" in res_data
    assert b'<form name="product_form"' in res_data
```

To check creating we use our `admin_login` helper to set up our session, then load the `/create-product` URL and check that our form is there.

For editing we first need a product, so we create one using the helper. We then visit the admin URL for that product and check the name and price are shown, as well as the form.

```python
@with_test_db((Product,))
def test_save_product_as_create():
    admin_login()

    assert Product.select().count() == 0

    form_data = {"name": "Floss", "price": "1.50"}

    testing_app.post("/admin/save-product", data=form_data)

    assert Product.select().count() == 1

    p = Product.get()
    assert p.name == "Floss"
    assert p.price == "1.50"


@with_test_db((Product,))
def test_save_product_as_edit():
    admin_login()

    p = create_test_product("Toothbrush", "2.99")

    assert Product.select().count() == 1

    form_data = {"product_id": p.id, "name": "Floss", "price": "1.50"}

    testing_app.post("/admin/save-product", data=form_data)

    assert Product.select().count() == 1

    p = Product.get()
    assert p.name == "Floss"
    assert p.price == "1.50"
```
We test saving in the context of both a create and an edit. For create we first check there are no instances in our database, using Peewee's `select().count()`, then POST some form data to our `/save-product` URL. We now check that the database has an entry, and that the data in that entry is the same as from our form data.

Updating requires an existing product, so we create one and assert that it's the only record in our database. Then we post form data with different values and check that a new instance was _not_ created. We finish by asserting that the form data has replaced the original data for this record.

```python
@with_test_db((Product,))
def test_delete_product():
    admin_login()

    p = create_test_product("Floss", "1.50")

    assert Product.select().count() == 1

    form_data = {"product_id": p.id}

    testing_app.post("/admin/delete-product", data=form_data)

    assert Product.select().count() == 0
```

Finally, deleting a product is tested by creating an instance then POSTing its ID to our `/delete-product` URL. We then check that the row has been removed from our database. 

Great, that's all of our admin section tested! We can now be sure that adding new functionality won't change the expected behaviour of any of these URLs. 

### Testing the Shop

Since we last wrote tests for the shop we've added a Cart and Checkout functionality. Let's get tests for these features going. Open up `tests/site/test_site.py`:

```python
@with_test_db((Product,))
def test_add_product_to_cart():
    p = create_test_product("Floss", "1.50")
    p2 = create_test_product("Toothbrush", "2.99")

    with testing_app as app_with_session:
        app_with_session.get("/")

        from flask import session

        assert "cart" in session
        assert session["cart"] == []

        res = app_with_session.post("/add-product-to-cart", data={"product_id": p.id})

        assert session["cart"] == [p.id]
        assert res.get_json()["cart_items"] == 1

        res = app_with_session.post("/add-product-to-cart", data={"product_id": p2.id})

        assert session["cart"] == [p.id, p2.id]
        assert res.get_json()["cart_items"] == 2
```

In order to test our Cart we need some products to add to it, so we create two using our helper. 

The Flask session is not usually available to be imported in tests, but we can use a `with` block around our `testing_app` which will allow us to import and check the contents of the `session` whilst inside.

Using this, we fire a request to the index page in order to create an empty `cart` in our `session`. We can then import this `session` and check for its presence. 

A couple of requests to `/add-product-to-cart` are fired off and the `session`'s `cart` is checked for their IDs.

```python
@with_test_db((Order, Product))
def test_checkout_get():
    p = create_test_product("Floss", "1.50")
    p2 = create_test_product("Toothbrush", "2.99")

    with testing_app.session_transaction() as s:
        s.clear()
        s["cart"] = [p.id, p.id, p2.id]

    res = testing_app.get("/checkout")
    res_data = res.get_data()

    assert b"Floss" in res_data
    assert b"Toothbrush" in res_data
    assert b"3.00" in res_data
    assert b"2.99" in res_data
```

To test our Checkout page we create two products and use a `session_transaction` to put them into our Cart. We then load the `/checkout` page and get its contents. The names and prices of our products are checked for inside (we look for `"3.00"` since we have 2 instances of our Floss at 1.50). 

```python
@with_test_db((Order, Product))
def test_checkout_post():
    p = create_test_product("Floss", "1.50")
    p2 = create_test_product("Toothbrush", "2.99")

    assert Order.select().count() == 0

    with testing_app.session_transaction() as s:
        s.clear()
        s["cart"] = [p.id, p.id, p2.id]

    res = testing_app.post(
        "/checkout", data={"email": "a@a.com"}, follow_redirects=True
    )
    res_data = res.get_data()

    assert b"Floss" in res_data
    assert b"Toothbrush" in res_data
    assert b"3.00" in res_data
    assert b"2.99" in res_data
    assert b"sent to a@a.com" in res_data

    assert Order.select().count() == 1

    o = Order.get()
    assert o.email == "a@a.com"
    assert o.products == {
        "Floss": {"total": 3.0, "quantity": 2},
        "Toothbrush": {"total": 2.99, "quantity": 1},
    }
```

Placing an order is done by a POST request to `/checkout` with products in our Cart and an email address sent via the form. We begin by creating our products again and adding them to our Cart. We also check the `Order` table to ensure it's empty. 

After our POST request containing our email address, we check again for the same product information, as well as the email confirmation message. 

We finish by ensuring the `Order` has been created, and check it holds the correct data.

With that, our site is fully tested! We have the ability to quickly and easily check that the core behaviours of our site and admin remain intact as we add or remove features. 

To finish off our project, we will have a brief look at how we can run code which makes use of our site's data but outside of the context of a web request, using a library called Celery. 
