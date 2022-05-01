from flask import Flask
from celery import Celery

app = Flask(__name__)
app.secret_key = "very secret"

celery = Celery("My Shop", broker="memory://")

from web.views import admin, site
from web.blueprints import site_blueprint, admin_blueprint

app.register_blueprint(site_blueprint)
app.register_blueprint(admin_blueprint)

app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE="True")


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
