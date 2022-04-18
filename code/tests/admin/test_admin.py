from models.admin_user import AdminUser
from models.product import Product
from tests.helpers import *
from tests import testing_app


def admin_login():
    with testing_app.session_transaction() as s:
        s.clear()
        s["logged_in"] = True
        s["admin_user_id"] = 1


def test_index_redirects_to_login_if_not_logged_in():
    res = testing_app.get("/admin/")

    assert res.status_code == 302
    assert b"/login" in res.get_data()


def test_index_does_not_redirect_if_logged_in():
    with testing_app.session_transaction() as s:
        s.clear()
        s["logged_in"] = True
        s["admin_user_id"] = 1

    res = testing_app.get("/admin/")

    assert res.status_code == 200


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


@with_test_db((Product,))
def test_delete_product():
    admin_login()

    p = create_test_product("Floss", "1.50")

    assert Product.select().count() == 1

    form_data = {"product_id": p.id}

    testing_app.post("/admin/delete-product", data=form_data)

    assert Product.select().count() == 0
