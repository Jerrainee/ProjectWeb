from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed


class CommentForm(FlaskForm):
    content = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Отправить')
