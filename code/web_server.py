from flask import Flask, render_template, abort
from models.product import Product

app = Flask(__name__)
app.secret_key = "very secret"


@app.route("/")
def index():
    products = Product.select()
    return render_template("index.html", products=products)


@app.route("/<string:product_name>")
def view_product(product_name):
    product = Product.get_or_none(Product.name == product_name)

    if not product:
        return abort(404)

    return render_template(
        "products/view_product.html", price=product.price, product_name=product_name
    )


if __name__ == "__main__":
    app.run(debug=True)
