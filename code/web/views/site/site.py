from flask import abort, render_template, session, request

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

    return render_template("products/view_product.html", product=product)


@site_blueprint.route("/add-product-to-cart", methods=["POST"])
def add_product_to_cart():
    product_id = request.form.get("product_id")
    if not product_id:
        return {"success": False, "cart_items": len(session["cart"])}

    current_cart = session["cart"]
    current_cart.append(product_id)

    session["cart"] = current_cart

    return {"success": True, "cart_items": len(session["cart"])}


@site_blueprint.route("/checkout")
def checkout():
    if request.method == "POST":
        pass

    cart_items = []
    cart_products = {}
    total_price = 0
    for product_id in session["cart"]:
        p = Product.get_or_none(Product.id == product_id)
        if p.name not in cart_products:
            cart_products[p.name] = {"total": float(p.price), "quantity": 1}
        else:
            cart_products[p.name]["total"] += float(p.price)
            cart_products[p.name]["quantity"] += 1

    for name, price_info in cart_products.items():
        cart_items.append(
            {
                "name": name,
                "quantity": price_info["quantity"],
                "total_price": price_info["total"],
            }
        )
        total_price += price_info["total"]

    return render_template(
        "checkout.html", cart_items=cart_items, total_price=total_price
    )
