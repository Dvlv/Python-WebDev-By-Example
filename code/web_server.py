from flask import Flask

app = Flask(__name__)
app.secret_key = "very secret"

from web.views import admin, site
from web.blueprints import site_blueprint, admin_blueprint

app.register_blueprint(site_blueprint)
app.register_blueprint(admin_blueprint)


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
