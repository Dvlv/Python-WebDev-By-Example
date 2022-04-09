from flask import request, session, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash

from models.admin_user import AdminUser
from models.product import Product
from web.blueprints import admin_blueprint


@admin_blueprint.route("/")
def admin_index():
    all_products = Product.select().order_by(Product.name.asc())

    return render_template("admin/index.html", all_products=all_products)


@admin_blueprint.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = AdminUser.get_or_none(AdminUser.username == username)
        if user:
            password_correct = check_password_hash(user.password, password)

            if password_correct:
                session["logged_in"] = True
                session["admin_user_id"] = user.id

                return redirect(url_for("admin.admin_index"))
            else:
                flash("Please try again!")

        else:
            flash("Please try again")

    return render_template("admin/login.html")


@admin_blueprint.route("/create-product")
def create_product():
    return render_template("/admin/products/create_product.html")


@admin_blueprint.route("/<int:product_id>")
def edit_product(product_id: int):
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash("Product not found")

        return redirect(url_for("admin.admin_index"))

    return render_template("admin/products/edit_product.html", product=product)


@admin_blueprint.route("/save-product", methods=["POST"])
def save_product():
    product = Product()

    product_id = request.form.get("product_id")
    if product_id:
        product = Product.get_or_none(Product.id == product_id)
        if not product:
            return redirect(url_for("admin.admin_index"))

    name = request.form.get("name")
    price = request.form.get("price")

    product.name = name
    product.price = price
    product.save()

    return redirect(url_for("admin.edit_product", product_id=product.id))


@admin_blueprint.route("/delete-product", methods=["POST"])
def delete_product():
    product_id = request.form.get("product_id")
    if product_id:
        product = Product.get_or_none(Product.id == product_id)
        if not product:
            return {"success": False, "message": "Product not found"}, 400

    Product.delete().where(Product.id == product_id).execute()

    return {"success": True, "message": "Product Deleted"}
