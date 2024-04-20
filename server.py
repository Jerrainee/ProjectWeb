import datetime

import requests
from flask import Flask, render_template, redirect, request, flash, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from TestAdd.addTestData import add_tests
from data import db_session
from data.forum_posts import ForumPost
from data.forum_messages import Message
from data.news import News
from data.tests_comments import Comment
from data.support import SupportMessage
from forms.user import RegisterForm, LoginForm, ProfileForm
from forms.test_form import TestForm
from forms.comment import CommentForm
from forms.post_news_form import PostNewsForm
from forms.thread_form import CreateThreadForm, WriteMessageForm

from test_functional import TestFunc
from data.users import User
from data.tests import Test

import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)

cur_res = dict()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/result')
def result():
    search_query = request.args.get('search').split()
    db_sess = db_session.create_session()
    res = []
    tests = db_sess.query(Test).all()
    for i in tests:
        cur_search = ' '.join([str(i).lower() for i in str(i).split(';;')[1].split()])
        for word in search_query:
            if word.lower() in cur_search and i not in res:
                res.append(i)
            elif word.lower() not in cur_search:
                break
    res = [i for i in res[::-1]]
    if len(res) > 9:
        res = res[:9]

    return render_template('search.html', tests=res, request=' '.join(search_query))


@app.route('/')
@app.route('/home')
def home():
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).all()
    print(tests[-1].id)
    return render_template('main.html', tests=tests)


@app.route('/account')
def profile():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        cur_user = db_sess.query(User).get(current_user.get_id())
        dct = {}
        if cur_user.test_results:
            dct = eval(cur_user.test_results)
        return render_template('account.html', user=cur_user, dct=dct)
    return redirect('/login')


@app.route('/account/<int:i>')
def account(i):
    dct = {}
    db_sess = db_session.create_session()
    cur_user = db_sess.query(User).filter(User.id == i).first()
    if not cur_user:
        return abort(404)
    if cur_user.test_results:
        dct = eval(cur_user.test_results)
    return render_template('account.html', user=cur_user, dct=dct)


@app.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = ProfileForm()
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
            flash('Пользователь с таким ником уже существует!', 'error')
    return render_template('change_profile.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash('Пароли не совпадают!', 'error')
            return render_template('register.html', title='Регистрация', form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            flash('Такой пользователь уже есть!', 'error')
            return render_template('register.html', title='Регистрация', form=form)
        resp = requests.get("https://api.thecatapi.com/v1/images/search").json()[0]["url"]
        user = User(
            is_admin=0,
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            cat=resp
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
        flash('Неправильный логин или пароль!', 'error')
        return render_template('login.html', form=form)
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


@app.errorhandler(400)
def bad_request(_):
    return render_template('400.html'), 400


@app.route('/test/<int:i>')
def page(i):
    db_sess = db_session.create_session()
    cur_test = db_sess.query(Test).filter(Test.id == i).first()
    if not cur_test:
        return abort(404)
    return render_template('test_preview.html', test=cur_test)


@app.route('/test/<int:i>/result')
def result_page(i):
    global cur_res
    db_sess = db_session.create_session()
    cur_test = db_sess.query(Test).filter(Test.id == i).first()
    if not cur_test or not cur_res:
        return abort(400)
    res = TestFunc(cur_test).result(cur_res)
    if current_user.is_authenticated:
        cur_user = db_sess.query(User).get(current_user.get_id())
        if not cur_user.test_results:
            cur_user.test_results = '{}'
        dct = eval(cur_user.test_results)
        dct[i] = res
        cur_user.test_results = str(dct)
        db_sess.commit()
    cur_res = dict()
    return render_template('test_result.html', res=res, test=cur_test)


@app.route('/test/<int:i>/<int:n>', methods=['GET', 'POST'])
def test_run(i, n):

    global cur_res
    db_sess = db_session.create_session()
    cur_test = db_sess.query(Test).filter(Test.id == i).first()
    db_sess.close()
    if not cur_test:
        return abort(404)
    cur_query = TestFunc(cur_test)
    res = cur_query.run(n)
    if request.method == 'GET':
        if len(res) == 2:
            qst, ans = res
            form = TestForm()
            form.answers.label = qst
            form.answers.choices = [(i, ans[i]) for i in ans.keys()]
            return render_template('test_run.html', form=form, n=(n + 1), length=len(cur_query.data))
        elif res == '1':
            return redirect(f'/test/{i}/result')
    elif request.method == 'POST':
        if not request.form.get('answers'):
            flash('Пожалуйста, выберите вариант ответа!', 'error')
            return redirect(f'/test/{i}/{n}')
        cur_res[res[0]] = int(request.form.get('answers'))
        print(request.form.get('answers'))
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
            return abort(401)
        return redirect(f'/test/{i}')
    return render_template('write_comment.html', form=form)


@app.route('/comment_delete/<int:i>')
def delete_comment(i):
    db_sess = db_session.create_session()
    cur_comm = db_sess.query(Comment).filter(Comment.id == i).first()
    cur_test = cur_comm.test.id
    if cur_comm and int(current_user.get_id()) == cur_comm.author_id:
        db_sess.delete(cur_comm)
        db_sess.commit()
    else:
        return abort(404)
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
        msgs = db_sess.query(SupportMessage).all()
        return render_template('messages.html', msgs=msgs)


@app.route('/admin/messages/delete_message/<int:i>')
def delete_message(i):
    db_sess = db_session.create_session()
    db_sess.delete(db_sess.query(SupportMessage).get(i))
    db_sess.commit()
    return redirect('/admin/messages/')


@app.route('/admin/post_news', methods=['POST', 'GET'])
def admin_post_news():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.get_id())
    if user.is_admin != 1:
        flash('У вас нет доступа к этой странице!', 'error')
        return redirect('/')
    else:
        form = PostNewsForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                news = News()
                news.title = request.form.get('title')
                news.content = request.form.get('txt')
                news.author_id = user.id
                news.picture = base64.b64encode(form.file.data.read()).decode('ascii')
                db_sess.add(news)
                db_sess.commit()
                flash('Форма успешно добавлена', 'success')
                return redirect('/news')
            else:
                flash('Неподдерживаемый файл', 'error')
        return render_template('admin_post_news.html', form=form)


@app.route('/news')
def showNews():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return render_template('news.html', news=news)


@app.route('/forum')
def showForum():
    db_sess = db_session.create_session()
    posts = db_sess.query(ForumPost).all()
    return render_template('forum.html', branches=posts)


@app.route('/forum/<int:thread_id>')
def show_thread(thread_id):
    db_sess = db_session.create_session()
    thread = db_sess.query(ForumPost).get(thread_id)
    if thread:
        return render_template('thread.html', thread=thread)
    abort(404)

@app.route("/forum/post_delete/<int:i>")
def forum_post_delete(i):
    db_sess = db_session.create_session()
    cur_post = db_sess.query(ForumPost).filter(ForumPost.id == i).first()
    if cur_post and int(current_user.get_id()) == cur_post.author_id:
        post_messages = db_sess.query(Message).filter(Message.post_id == cur_post.id).all()
        db_sess.delete(cur_post)
        print(post_messages, 1231231234123)
        for mess in post_messages:
            db_sess.delete(mess)
        db_sess.commit()
    else:
        return abort(404)
    return redirect(f'/forum')



@app.route('/forum/create_thread', methods=['POST', 'GET'])
def create_thread():
    form = CreateThreadForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            new_thread = ForumPost()
            new_thread.title = request.form.get('title')
            new_thread.content = request.form.get('content')
            new_thread.author_id = current_user.get_id()
            new_thread.picture = base64.b64encode(form.file.data.read()).decode('ascii')
            db_sess.add(new_thread)
            db_sess.commit()
            flash('Форма успешно добавлена', 'success')
            return redirect('/forum')
        else:
            flash('Неподдерживаемый файл', 'error')
    if current_user.is_authenticated:
        return render_template('create_thread.html', form=form)
    return abort(401)

@app.route('/forum/message_delete/<int:i>')
def delete_forum_message(i):
    db_sess = db_session.create_session()
    cur_mess = db_sess.query(Message).filter(Message.id == i).first()
    cur_tread = cur_mess.post_id
    if cur_mess and int(current_user.get_id()) == cur_mess.author_id:
        db_sess.delete(cur_mess)
        db_sess.commit()
    else:
        return abort(404)
    return redirect(f'/forum/{cur_tread}')


@app.route('/forum/<int:thread_id>/write_message', methods=['POST', 'GET'])
def write_message(thread_id):
    form = WriteMessageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            new_message = Message()
            new_message.content = request.form.get('content')
            new_message.author_id = current_user.get_id()
            if form.file.data:
                new_message.picture = base64.b64encode(form.file.data.read()).decode('ascii')
            new_message.post_id = thread_id
            db_sess.add(new_message)
            db_sess.commit()
            flash('Форма успешно добавлена', 'success')
            return redirect(f'/forum/{thread_id}')
        else:
            flash('Неподдерживаемый файл', 'error')
    if current_user.is_authenticated:
        return render_template('write_message.html', form=form)
    return abort(401)


@app.route('/support', methods=["POST", "GET"])
def support():
    if request.method == "POST":
        db_sess = db_session.create_session()
        mes = SupportMessage()
        mes.author_id = current_user.get_id()
        mes.email = request.form.get('email')
        mes.author_name = request.form.get('name')
        mes.message = request.form.get('msg')
        db_sess.add(mes)
        db_sess.commit()
        db_sess.flush()
        flash('Сообщение успешно отправлено!', category="success")
        return redirect('/')
    return render_template("support.html")


def main():
    db_session.global_init("db/site_DB.db")
    db_sess = db_session.create_session()
    #add_tests(db_sess)
    app.run(debug=True)


if __name__ == '__main__':
    main()
