import sys

from celery import Celery
from flask import Flask

app = Flask(__name__)
app.secret_key = "very secret"

if "pytest" in sys.modules:
    celery = Celery("My Shop", broker="memory://")
else:
    celery = Celery("My Shop", broker="redis://localhost:6379/0")


from web.views import admin, site
from web.blueprints import site_blueprint, admin_blueprint

app.register_blueprint(site_blueprint)
app.register_blueprint(admin_blueprint)

app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE="True")


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
