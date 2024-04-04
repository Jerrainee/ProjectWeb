from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):

    def __init__(self, question, answers):
        super().__init__()
        self.question = question
        self.answers = [(i, i) for i in answers.keys()]

    def run_form(self):
        answers = RadioField(self.question, choices=self.answers)
        submit = SubmitField('Ответить')
