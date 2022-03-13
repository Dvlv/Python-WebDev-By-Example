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
