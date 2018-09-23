from flask import Blueprint

game_blueprint = Blueprint("game", __name__, url_prefix="/game")

record_blueprint = Blueprint("record", __name__, url_prefix="/record")

runner_blueprint = Blueprint("runner", __name__, url_prefix="/runner")
