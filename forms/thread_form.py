from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CreateThreadForm(FlaskForm):
    thread_title = StringField('Заголовок треда', validators=[DataRequired()], name="title")
    tread_content = TextAreaField('Описание', name="content", validators=[DataRequired()])
    file = FileField(validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])], name='file')
    submit = SubmitField('Создать')


class WriteMessageForm(FlaskForm):
    message_content = StringField('Содержимое сообщения', validators=[DataRequired()], name="content",
                                  description='Введите сообщение')
    file = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'])], name='file')
    submit = SubmitField('Создать')