from flask import request, session, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash

from models.admin_user import AdminUser
from web.blueprints import admin_blueprint


@admin_blueprint.route("/")
def admin_index():
    return render_template("admin/index.html")


@admin_blueprint.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = AdminUser.get_or_none(AdminUser.username == username)
        if not user:
            return False

        password_correct = check_password_hash(user.password, password)
        if password_correct:
            session["logged_in"] = True
            session["admin_user_id"] = user.id

            return redirect(url_for("admin.admin_index"))
        else:
            flash("Please try again!")

    return render_template("admin/login.html")
