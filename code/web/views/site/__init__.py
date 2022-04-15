from . import site
from web.blueprints import site_blueprint


@site_blueprint.context_processor
def inject_variables():
    from flask import session

    if "cart" not in session:
        session["cart"] = []

    return {"cart": session["cart"]}
