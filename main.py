import datetime

import wtforms
from flask import Flask, render_template, redirect, request, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from data import db_session
from TestAdd.addTestData import add_tests, add_test_users
from data.forum_posts import ForumPost
from data.news import News
from data.tests_comments import Comment
from forms.user import RegisterForm, LoginForm, ProfileForm
from forms.test_form import TestForm
from forms.comment import CommentForm

from test_functional import TestFunc
from data.users import User
from data.tests import Test
from data.forum_messages import Message
from UserLogin import UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)

cur_res = []


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def home():
    if request.method == 'GET':
        return render_template('main.html')
    else:
        print(request.form.get('search'))
        return ''


@app.route('/account', methods=['GET', 'POST'])
def profile():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        cur_user = db_sess.query(User).get(current_user.get_id())
        dct = {}
        if cur_user.test_results:
            dct = eval(cur_user.test_results)
        return render_template('account.html', user=cur_user, dct=dct)
    return redirect('/login')


@app.route('/account/<int:i>', methods=['GET', 'POST'])
def account(i):
    dct = {}
    db_sess = db_session.create_session()
    cur_user = db_sess.query(User).filter(User.id == i).first()
    if cur_user.test_results:
        dct = eval(cur_user.test_results)
    return render_template('account.html', user=cur_user, dct=dct)


@app.route('/change_profile', methods=['GET', 'POST'])
def change_profile():
    if current_user.is_authenticated:
        form, message = ProfileForm(), ''
        db_sess = db_session.create_session()
        cur_user = db_sess.query(User).get(current_user.get_id())
        if request.method == 'GET':
            form.name.data = cur_user.name
            form.about.data = cur_user.about

        elif request.method == 'POST':
            check = db_sess.query(User).filter(User.name == form.name.data).first()
            if not check or check == cur_user:
                cur_user.name = form.name.data
                cur_user.about = form.about.data
                db_sess.commit()
                return redirect('/account')
            else:
                message = 'Пользователь с таким ником уже существует!'
        return render_template('change_profile.html', form=form, message=message)


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
            is_admin=0,
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def not_authorized(e):
    return render_template('401.html'), 401


@app.route('/test/<int:i>', methods=['GET', 'POST'])
def page(i):
    db_sess = db_session.create_session()
    cur_test = db_sess.query(Test).filter(Test.id == i).first()
    return render_template('test_preview.html', test=cur_test)


@app.route('/test/<int:i>/result', methods=['GET', 'POST'])
def result_page(i):
    global cur_res
    db_sess = db_session.create_session()
    cur_test = db_sess.query(Test).filter(Test.id == i).first()
    res = TestFunc(cur_test).result(cur_res)
    if current_user.is_authenticated:
        cur_user = db_sess.query(User).get(current_user.get_id())
        if not cur_user.test_results:
            cur_user.test_results = '{}'
        dct = eval(cur_user.test_results)
        dct[i] = res
        cur_user.test_results = str(dct)
        db_sess.commit()
    cur_res = []

    return render_template('test_result.html', res=res, test=cur_test)


@app.route('/test/<int:i>/<int:n>', methods=['GET', 'POST'])
def test_run(i, n):
    global cur_res
    if request.method == 'GET':
        db_sess = db_session.create_session()
        cur_test = db_sess.query(Test).filter(Test.id == i).first()
        cur_query = TestFunc(cur_test)
        res = cur_query.run(n)
        if len(res) == 2:
            qst, ans = res
            form = TestForm()
            form.answers.label = qst
            form.answers.choices = [(i, ans[i]) for i in ans.keys()]
            return render_template('test_run.html', form=form)
        elif res == '1':
            return redirect(f'/test/{i}/result')
    elif request.method == 'POST':
        cur_res.append(int(request.form.get('answers')))
        return redirect(f'/test/{i}/{n + 1}')


@app.route('/write_comment/<int:i>', methods=['GET', 'POST'])
def write_comment(i):
    form = CommentForm()
    if request.method == "POST":
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            comment = Comment(
                content=form.content.data,
                author_id=current_user.id,
                test_id=i,
                date_of_creation=datetime.datetime.now()
            )
            db_sess.add(comment)
            db_sess.commit()
        else:
            flash("Пожалуйста, войдите в аккаунт", "error")
        return redirect(f'/test/{i}')
    return render_template('write_comment.html', form=form)


@app.route('/comment_delete/<int:i>', methods=['GET', 'POST'])
def delete_comment(i):
    db_sess = db_session.create_session()
    cur_comm = db_sess.query(Comment).filter(Comment.id == i).first()
    cur_test = cur_comm.test.id
    if cur_comm:
        db_sess.delete(cur_comm)
        db_sess.commit()
    return redirect(f'/test/{cur_test}')

@app.route('/admin/')
@login_required
def admin():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.get_id())
    if user.is_admin != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect('/')
    else:
        return render_template('admin.html')

@app.route('/admin/messages/')
@login_required
def admin_messages():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.get_id())
    if user.is_admin != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect('/')
    else:
        return render_template('messages.html')

@app.route('/admin/post_news', methods = ['POST', 'GET'])
def admin_post_news():
    # Необходимо реализовать функционал проверки на доступ к админской панели через проверку условия из БД. отображать ошибку доступа при переходе на главную страницу, нужен функционал добавления новости


    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.get_id())
    if user.is_admin != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect('/')
    else:
        if request.method == "POST":
           pass # нужна форма создания новости, html перепиши !
    return render_template('admin_post_news.html')

@app.route('/news')
def showNews():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return render_template('news.html', news=news)

@app.route('/forum')
def showForum():
    # необходимо сделать переход к посту, чтоб там были комменты

    db_sess = db_session.create_session()
    posts = db_sess.query(ForumPost).all()

    return render_template('forum.html', posts=posts)

@app.route('/support', methods = ["POST", "GET"])
def support():
    # Необходимо реализовать функционал добавления и отправки сообщения через sqlalchemy
    # ДОБАВЬТЕ ТАБЛИЦУ С ОБРАЩЕНИЯМИ
    '''
    if request.method == "POST":
        # code here

        # --- --- ---
        res = # вызов булевой функции, подтверждающей отправление сообщения
        if res:
            flash('Сообщение успешно отправлено!', category="success")
        else:
            flash('Не удалось отправить сообщение!','error')
    '''
    return render_template("support.html")

def main():
    db_session.global_init("db/site_DB.db")
    db_sess = db_session.create_session()
    add_tests(db_sess)
    app.run(debug=True)


if __name__ == '__main__':
    main()
