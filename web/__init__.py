from flask import Flask

from web import views
from web.views.blueprints import game_blueprint

app = Flask(__name__)
app.debug = True
app.secret_key = "supersecret"

app.register_blueprint(game_blueprint)



