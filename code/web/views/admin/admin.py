from flask import request, session, render_template, redirect, url_for
from werkzeug.security import check_password_hash

from models.admin_user import AdminUser
from web.blueprints import admin_blueprint


@admin_blueprint.route("/")
def admin_index():
    if not session.get("logged_in"):
        return redirect(url_for("admin.admin_login"))

    return "Welcome to the admin"


@admin_blueprint.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = AdminUser.get_or_none(AdminUser.username == username)
        if not user:
            return False

        password_correct = check_password_hash(user.password, password)

        if not password_correct:
            return False

        session["logged_in"] = True
        session["admin_user_id"] = user.id

        return redirect(url_for("admin.admin_index"))

    return "please log in"
