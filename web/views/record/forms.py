from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired

from models.runner import Runner
from models.game import Game

runners = Runner.get_all()
games = Game.get_all()


class RecordForm(FlaskForm):
    game = SelectField("Game", choices=games)
    runner = SelectField("Runner", choices=runners)
    time = StringField("Time", validators=[DataRequired()])
    verified = BooleanField("Verified")