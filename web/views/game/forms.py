from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired

platforms = (
    ("NES", "NES"),
    ("SNES", "SNES"),
    ("PS1", "PS1"),
    ("PS2", "PS2"),
    ("PS3", "PS3"),
    ("Gamecube", "Gamecube"),
    ("Xbox", "Xbox"),
    ("Wii", "Wii"),
    ("Wii U", "Wii U"),
    ("Xbox 360", "Xbox 360"),
    ("Xbox One", "Xbox One"),
    ("PS4", "PS4"),
    ("Switch", "Switch"),
)


class GameForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    platform = SelectField("Platform", choices=platforms, validators=[DataRequired()])
    release_year = IntegerField("Release Year", validators=[DataRequired()])
    save = SubmitField("Save")