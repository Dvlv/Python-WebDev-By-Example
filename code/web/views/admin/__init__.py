from flask import request, session, redirect, url_for

from web.blueprints import admin_blueprint

from . import admin


@admin_blueprint.before_request
def admin_before_request():
    if request.endpoint != "admin.admin_login":
        if "logged_in" not in session:
            return redirect(url_for("admin.admin_login"))
