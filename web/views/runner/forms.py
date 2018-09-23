from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class RunnerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    country = StringField("Country")

