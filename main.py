import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager

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


@app.route('/test_run/<int:n>', methods=['GET', 'POST'])
def test_run(n):
    a = Test('test1.json')
    res = a.run(n)
    if len(res) == 2:
        qst, ans = res
        form = TestForm(qst, ans).run_form()
        render_template('test_run.html', form=form)


def main():
    db_session.global_init("db/site_DB.db")
    db_sess = db_session.create_session()
    app.run(debug=True)


if __name__ == '__main__':
    main()
