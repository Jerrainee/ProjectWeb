from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired


class PostNewsForm(FlaskForm):
    news_title = StringField('Название новости', validators=[DataRequired()], name="title")
    news_text = TextAreaField('Текст новости', name="txt", validators=[DataRequired()])
    file = FileField(validators=[DataRequired()], name='file')
    submit = SubmitField('Войти')