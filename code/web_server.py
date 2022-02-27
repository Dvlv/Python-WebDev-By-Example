from flask import Flask, render_template, abort

app = Flask(__name__)
app.secret_key = "very secret"


@app.route("/")
def index():
    products = {"toothpaste": 2.00, "toothbrush": 1.50, "floss": 0.99}
    return render_template("index.html", products=products)


@app.route("/<string:product_name>")
def view_product(product_name):
    products = {"toothpaste": 2.00, "toothbrush": 1.50, "floss": 0.99}

    price = None
    if product_name in products:
        price = products[product_name]
    else:
        abort(404)

    return render_template(
        "products/view_product.html", price=price, product_name=product_name
    )


if __name__ == "__main__":
    app.run(debug=True)
