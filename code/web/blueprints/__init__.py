from flask import Blueprint

site_blueprint = Blueprint("site", __name__)
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")
