from flask import Flask, render_template, request, g, flash, session, redirect, url_for
import os
import sqlite3
import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

# -- Configuration --
SECRET_KEY = '5728587e3f3ec902535e6ca60e1e98f7065dab376a661e05'
DEBUG = True
DATABASE = 'N/A'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'data.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


global dbase
dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    db = get_db()
    global dbase
    dbase = FDataBase.FDataBase(db)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/", methods=["POST", "GET"])
def main():
    return render_template('main.html')


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/support', methods=["POST", "GET"])
@login_required
def support():
    if request.method == "POST":
        id = current_user.id
        msg = request.form['msg']
        res = dbase.sendMsg(id, msg)
        if res:
            flash('Сообщение успешно отправлено!', category="success")
        else:
            flash('Не удалось отправить сообщение!', 'error')

    return render_template("support.html")


@app.route('/admin/post_news', methods=['POST', 'GET'])
def admin_post_news():
    db = get_db()
    dbase = FDataBase.FDataBase(db)
    user = dbase.getUser(current_user.id)
    if user['IsAdmin'] != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect(url_for('main'))
    else:
        if request.method == "POST":
            img = request.files['image']
            res = dbase.addNews(request.form['title'], request.form['txt'], img)
            flash('Новость успешно добавлена', category="success")

    return render_template('admin_post_news.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/news')
def showNews():
    db = get_db()
    dbase = FDataBase.FDataBase(db)
    based = dbase.getNews()
    return render_template('news.html', news=based[::-1])


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUser(request.form['id'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2'] and \
                dbase.getUser(request.form['id'])['psw'] == ".":
            id = request.form['id']
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(id, hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля (Не совпадает пароль / Такого пользователя не существует)", "error")

    return render_template("register.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=dbase.getUser(current_user.id))


@app.route('/admin/')
@login_required
def admin():
    user = dbase.getUser(current_user.id)
    if user['IsAdmin'] != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect(url_for('main'))
    else:
        return render_template('admin.html')


if __name__ == "__main__":
    app.run(debug=True)
