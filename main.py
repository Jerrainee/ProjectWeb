import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager

from data import db_session
from forms.user import RegisterForm, LoginForm

from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/home')
def home():
    return  # главная стр


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/site_DB.db")
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
