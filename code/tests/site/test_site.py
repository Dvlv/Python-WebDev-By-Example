from models.order import Order
from models.product import Product
from tests import testing_app
from tests.helpers import *


@with_test_db((Product,))
def test_index_displays_product_names():
    create_test_product("Toothbrush", "2.00")
    create_test_product("Toothpaste", "1.00")

    res = testing_app.get("/")

    assert res.status_code == 200

    res_data = res.get_data().decode("utf-8")
    assert "Toothbrush" in res_data
    assert "Toothpaste" in res_data


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
