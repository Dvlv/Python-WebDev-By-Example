from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired

platforms = (
    "NES",
    "SNES",
    "PS1",
    "PS2",
    "PS3",
    "Gamecube",
    "Xbox",
    "Wii",
    "Wii U",
    "Xbox 360",
    "Xbox One",
    "PS4"
    "Switch",
)


class GameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    platform = SelectField("Platform", choices=platforms, validators=[DataRequired()])
    release_year = IntegerField("Release Year", validators=[DataRequired()])