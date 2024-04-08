import datetime

import wtforms
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user

from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.test_form import TestForm

from test_functional import Test
from data.users import User
from UserLogin import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def home():
    return render_template('main.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/test_run/<int:n>', methods=['GET', 'POST'])
def test_run(n):
    if request.method == 'GET':
        a = Test('test1.json')
        res = a.run(n)
        if len(res) == 2:
            qst, ans = res
            form = TestForm()
            form.answers.label = qst
            form.answers.choices = ans
            return render_template('test_run.html', form=form)
    elif request.method == 'POST':
        print(request.form.get('answers'))
        return '' # сделать переход на следующую страницу


def main():
    db_session.global_init("db/site_DB.db")
    db_sess = db_session.create_session()
    app.run(debug=True)


if __name__ == '__main__':
    main()
