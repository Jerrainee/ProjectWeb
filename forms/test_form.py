from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    answers = RadioField('', choices=[])
    submit = SubmitField('Ответить')
