import datetime
import sqlite3
import os

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from TDataBase import TDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

# конфигурация
DATABASE = '/tmp/testsite.db'
DEBUG = True
SECRET_KEY = '150ce8e0c7df5b4797e90fdaa23c715171529b20'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
# app.permanent_session_lifetime = datetime.timedelta(days=0)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'testsite.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизируйтесь для доступа на страницу'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('loader_user')
    return UserLogin().fromDB(user_id, dbase)


def connetc_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connetc_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединенеи с БД, если оно ещё не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connetc_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Устанавливаем соединение с БД до выполнения запроса"""
    global dbase
    db = get_db()
    dbase = TDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    """Передача допольнительных параметров в headers текст"""
    # content = render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnnonce())
    # res = make_response(content)
    # res.headers['Content-Type'] = 'text/plain'
    # res.headers['Server'] = 'testsite'
    '''Передача допольнительных параметров в headers изображение'''
    # img = None
    # with app.open_resource(app.root_path + "/static/images/default.png", mode="rb") as f:
    #     img = f.read()
    #
    # if img is None:
    #     return "None image"
    #
    # res = make_response(img)
    # res.headers['Content-Type'] = 'image/png'
    '''Передача текста с кодом'''
    # res = make_response("<h1>Ошибка сервера</h1>", 500)

    # return "<h1>Main page</h1>", 200, {'Content-Type': 'text/plain'}
    '''Обновление сессии'''
    # if 'visit' in session:
    #     session['visit'] = session.get('visit') + 1 #обновление данных сессии
    # else:
    #     session['visit'] = 1 #запись данных сессии
    # return f"<h1>Main page</h1><p>Число просмотров: {session['visit']}</p>"
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnnonce())


'''Обновление сессии содержащей изменяющийся объект'''


# data = [1, 2, 3, 4]
# @app.route("/session")
# def session_data():
#     session.permanent = True
#     if 'data' not in session:
#         session['data'] = data
#     else:
#         session['data'][1] += 1
#         session.modified = True
#
#     return f"session['data']: {session['data']}"


@app.route("/add_post", methods=["POST", "GET"])
def addPosts():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.html', menu=dbase.getMenu(), title='Добавление статьи')


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route('/transfer')
def transfer():
    return redirect(url_for('index'), 301)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            login_user(userlogin, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('profile'))

        flash("Введен неверный пароль или логин", 'error')

    return render_template('login.html', menu=dbase.getMenu(), form=form, title="Авторизация")

    """Реализация формы без использования flask_wtforms"""
    # if request.method == "POST":
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get('next') or url_for('profile'))
    #
    #     flash("Введен неверный пароль или логин", 'error')
    #
    # return render_template('login.html', menu=dbase.getMenu(), title='Авторизация')
    '''Установка параметров для cookie'''
    # log = ""
    # if request.cookies.get("logged"):
    #     log = request.cookies.get("logged")
    #
    # res = make_response(f"<h1>Форма авторизации</h1><p>logged: {log}")
    # res.set_cookie("logged", "yes", 30*24*3600)
    # return res


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw1.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template('register.html', menu=dbase.getMenu(), title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка при добавлении в БД", "error")
                flash("Аватар обновлен", "success")
            except:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

        return redirect(url_for('profile'))


@app.errorhandler(404)
def pageNotFound(error):
    return "Страница не найдена", 404


#
# menu = [{"name": "Главная страница", "url": "main-page"},
#         {"name": "О компании", "url": "about"},
#         {"name": "Контакты", "url": "contacts"}]
#
# @app.route("/index")
# @app.route("/")
# def index():
#     print(url_for('index'))
#     return render_template('index.html', menu=menu)
#
# @app.route("/about")
# def about():
#     print(url_for('about'))
#     return render_template('about.html', title='О компании', menu=menu)
#
# @app.route("/profile/<username>")
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#
#     return f'Пользователь: {username}'
#
# @app.route("/contacts", methods=["POST", "GET"])
# def contacts():
#     if request.method == 'POST':
#         if len(request.form['username']) > 2:
#             flash('Сообщение отправленно', category='success')
#         else:
#             flash('Ошибка отправки', category='error')
#         return render_template('contacts.html', title='Контакты', menu=menu)
#
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if "userLogged" in session:
#         return redirect(url_for('profile', username=session['userLogged']))
#     elif request.method == 'POST' and request.form['username'] == "root" and request.form['psw'] == "root":
#         session['userLogged'] = request.form['username']
#         return redirect(url_for('profile', username=session['userLogged']))
#
#     return render_template('login.html', title="Авторизация", menu=menu)
#
#
# # with app.test_request_context():
# #     print(url_for('index'))
# #     print(url_for('about'))
# #     print(url_for('profile', username='maksim'))

if __name__ == "__main__":
    app.run(debug=True)
