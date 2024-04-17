from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostNewsForm(FlaskForm):
    news_title = StringField('Название новости', validators=[DataRequired()], name="title")
    news_text = TextAreaField('Текст новости', name="txt", validators=[DataRequired()])
    file = FileField(validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])], name='file')
    submit = SubmitField('Войти')