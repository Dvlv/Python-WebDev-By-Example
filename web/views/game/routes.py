from flask import render_template, request, flash

from models.game import Game
from web.views.blueprints import game_blueprint
from web.views.game.forms import GameForm


@game_blueprint.route("/create", methods=["GET", "POST"])
def create():
    game = Game()
    form = GameForm(obj=game)

    if request.method == "POST" and form.validate():
        game.update_from_form(request.form)
        flash("Game Created!")

    return render_template(
        "game/create_form.html",
        form=form
    )


@game_blueprint.route("/")
def index():
    all_games = Game.select()

    return render_template(
        "game/index.html",
        all_games=all_games
    )