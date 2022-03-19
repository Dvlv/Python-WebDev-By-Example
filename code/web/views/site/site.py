from flask import abort, render_template

from models.product import Product
from web.blueprints import site_blueprint


@site_blueprint.route("/")
def index():
    products = Product.select()
    return render_template("index.html", products=products)


@site_blueprint.route("/<string:product_name>")
def view_product(product_name):
    product = Product.get_or_none(Product.name == product_name)

    if not product:
        return abort(404)

    return render_template(
        "products/view_product.html", price=product.price, product_name=product_name
    )
