import json
import random

from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import orm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo

from data import db_session  # Импортируем базу данных ГеоКвиз
from data.riddles import Riddle  # Импортируем сущность загадка
from data.users import User  # Сущность пользователя
from data.found import Found  # Связь между загадками и пользователями

import logging

app = Flask(__name__)
login_manager = LoginManager()  # для аутентификации пользователей
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yan''dex''lyceum_secret_key'  # для шифрования паролей


logging.basicConfig(
    filename='log/main.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


@login_manager.user_loader
def load_user(user_id):  # Для загрузки пользователя
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/empty.js')
def empty_js():  # Получение скрипта с определением on_load по умолчанию
    return "function on_load() {}"


def get_marks():
    """
    Получение отметок карты для авторизованого ползователя.
    В зависимости от того, была ли найдена метка или нет, она будет отображаться разным цветом.
    """
    session = db_session.create_session()
    for riddle in session.query(Riddle).all():
        found = current_user.is_authenticated and session.query(Found)\
            .filter((Found.user_id == current_user.id) & (Found.riddle_id == riddle.id))
        yield f"{riddle.pos},pm{'gr' if found else 'wt'}m{riddle.id}"


@app.route('/map.js')
def map_js():  # Получение скрипта для отображения карты
    session = db_session.create_session()
    try:
        riddle = random.choice(tuple(session.query(Riddle).all()))
        long, latt = riddle.pos.split(',')
    except IndexError:
        long = latt = '0'
    with open('data/map.js') as f:
        return (f.read().replace('<marks>', '~'.join(get_marks()))
                .replace('<long>', long).replace('<latt>', latt))


@app.route('/to_page.js')
def to_page_js():  # Получение скрипта для перехода к страницам загадок и пользователей
    with open('data/to_page.js') as f:
        return f.read()


@app.route('/riddle_on_map.js')
def riddle_on_map_js():  # Получение скрипта для отображения загадки на карте
    with open('data/riddle_on_map.js') as f:
        return f.read()


@app.route('/riddle_on_map1.js')
def riddle_on_map1js():  # Получение скрипта для отображения редактируемой загадки на карте
    with open('data/riddle_on_map1.js') as f:
        return f.read()


@app.route("/new_riddle.js")
def new_riddle_js():  # Получения скрипта для загрузки координат новой загадки по умолчанию
    with open("data/new_riddle.js") as f:
        return f.read()


@app.route("/riddle.js")
def riddle_js():  # Получение скрипта для отображения загадки на карте
    with open("data/riddle.js") as f:
        return f.read()


class RegisterForm(FlaskForm):
    name = StringField('Имя:', validators=[DataRequired()])
    login = StringField('Логин:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password2 = PasswordField('Подтвердите пароль:', validators=[EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register():  # Регистрация нового пользователя
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title="Регистрация",
                                   message="Такой пользователь уже есть",
                                   form=form)
        user = User(name=form.name.data,
                    login=form.login.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        logging.info(f"Registered user {user.login}")
        return redirect('/')
    return render_template('register.html', title="Регистрация", form=form)


class LoginForm(FlaskForm):
    login = StringField('Логин:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():  # Вход
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title="Авторизация",
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():  # Выход из системы
    logout_user()
    return redirect("/")


def update_riddle_from_form(form, riddle):  # Обновление загадки
    long = float(form.long_deg.data) + (
            float(form.long_min.data) + float(form.long_sec.data) / 60) / 60
    latt = float(form.latt_deg.data) + (
            float(form.latt_min.data) + float(form.latt_sec.data) / 60) / 60
    riddle.pos = f'{long},{latt}'
    riddle.name = form.name.data
    riddle.desc = form.desc.data
    riddle.ans = form.ans.data


class NewRiddleForm(FlaskForm):
    latt_deg = StringField("", validators=[DataRequired()])
    latt_min = StringField("", validators=[DataRequired()], default="0")
    latt_sec = StringField("", validators=[DataRequired()], default="0")
    long_deg = StringField("", validators=[DataRequired()])
    long_min = StringField("", validators=[DataRequired()], default="0")
    long_sec = StringField("", validators=[DataRequired()], default="0")
    name = StringField("Название загадки:", validators=[DataRequired()])
    desc = StringField("Текст загадки:", validators=[DataRequired()])
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField('Создать')


@app.route("/new_riddle", methods=["GET", "POST"])
@login_required
def new_riddle():  # Создание загадки
    form = NewRiddleForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        riddle = Riddle()
        try:
            update_riddle_from_form(form, riddle)
        except ValueError:
            return render_template('edit_riddle.html', form=form, is_new=True,
                                   title="Создание загадки",
                                   message="Неверный формат координат")
        current_user.riddles.append(riddle)
        current_user.score += 5
        session.merge(current_user)
        session.commit()
        logging.info(f"Created riddle {riddle.id} by {current_user.login}")
        return redirect('/')
    return render_template('edit_riddle.html', form=form, is_new=True, title="Создание загадки")


class RiddleAnswerForm(FlaskForm):
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route('/riddles/<int:riddle_id>', methods=["GET", "POST"])
def riddle_page(riddle_id):  # Страница загадки
    session = db_session.create_session()
    try:
        riddle = session.query(Riddle).filter(Riddle.id == riddle_id).one()
    except orm.exc.NoResultFound:
        return render_template('missing_riddle.html', title='Такой загадки нет')
    form = RiddleAnswerForm()
    if form.validate_on_submit():
        if form.ans.data.lower() == riddle.ans.lower():
            message = "Правильно!"
            if current_user.is_authenticated and \
               not session.query(Found).filter((Found.user_id == current_user.id) &
                                               (Found.riddle_id == riddle.id)).all():
                new_found = Found()
                new_found.user_id = current_user.id
                new_found.riddle_id = riddle.id
                current_user.founds.append(new_found)
                current_user.score += 5
                session.merge(current_user)
                session.commit()
        else:
            message = "Неправильный ответ"
            if current_user.is_authenticated:
                current_user.score -= 1
                session.merge(current_user)
                session.commit()
        return render_template('riddle.html', riddle=riddle, form=form, message=message,
                               title=f"Загадка «{riddle.name}»")
    return render_template('riddle.html', riddle=riddle, form=form, title=f"Загадка «{riddle.name}»")


class RiddleEditForm(FlaskForm):
    latt_deg = StringField("", validators=[DataRequired()])
    latt_min = StringField("", validators=[DataRequired()], default="0")
    latt_sec = StringField("", validators=[DataRequired()], default="0")
    long_deg = StringField("", validators=[DataRequired()])
    long_min = StringField("", validators=[DataRequired()], default="0")
    long_sec = StringField("", validators=[DataRequired()], default="0")
    name = StringField("Название загадки:", validators=[DataRequired()])
    desc = StringField("Текст загадки:", validators=[DataRequired()])
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField('Сохранить')


@app.route('/riddles/<int:riddle_id>/edit', methods=["GET", "POST"])
@login_required
def edit_riddle(riddle_id):  # Редактирование загадки
    session = db_session.create_session()
    try:
        riddle = session.query(Riddle).filter(Riddle.id == riddle_id).one()
    except orm.exc.NoResultFound:
        return render_template('missing_riddle.html', title='Такой загадки нет')
    form = RiddleEditForm()
    can_edit = current_user.id == riddle.author_id
    if form.validate_on_submit():
        if not can_edit:
            return render_template('edit_riddle.html', form=form, title="Редактирование загадки",
                                   can_edit=can_edit,
                                   message="Вы вышли из аккаунта")
        try:
            update_riddle_from_form(form, riddle)
        except ValueError:
            return render_template('edit_riddle.html', form=form, title="Редактирование загадки",
                                   can_edit=can_edit,
                                   message="Неверный формат координат")
        session.merge(riddle)
        session.commit()
        logging.info(f"Edited riddle {riddle.id} by {current_user.login}")
        return redirect(f'/riddles/{riddle_id}')
    form.long_deg.default, form.latt_deg.default = riddle.pos.split(',')
    form.name.default = riddle.name
    form.desc.default = riddle.desc
    form.ans.default = riddle.ans
    form.process()
    return render_template('edit_riddle.html', form=form, title="Редактирование загадки",
                           can_edit=can_edit)


@app.route('/users/<user_login>')
def user_page(user_login):  # Страница пользователя
    session = db_session.create_session()
    try:
        user = session.query(User).filter(User.login == user_login).one()
        return render_template('user.html', user=user, title=f"Страница пользователя {user.name}")
    except orm.exc.NoResultFound:
        return render_template('missing_user.html', title="Страница несуществующего пользователя")


@app.route('/score-table')
def score_table():  # Таблица пользователей
    session = db_session.create_session()
    users = session.query(User).order_by(User.score.desc())
    return render_template('score_table.html', users=users, title="Положение")


@app.route('/help')
def help1():  # Страница с описанием игры
    return render_template('help.html', title="Как играть")


def format_pos(riddle):
    """
    Позиция загадки в формате широта,долгота с точностью до 5 знаков после точки
    """
    long, latt = (f'{float(coord):.5f}' for coord in riddle.pos.split(','))
    return f'{latt},{long}'


@app.route('/all-riddles')
def all_riddles():  # Страница всех загадок отсортированных по количеству решений
    session = db_session.create_session()
    riddles = sorted(session.query(Riddle).all(),
                     key=lambda riddle: len(riddle.founds),
                     reverse=True)
    return render_template('/all_riddles.html', title="Список загадок", riddles=riddles,
                           len=len, format_pos=format_pos)


@app.route('/')
def index():  # Главная страница
    return render_template('index.html', title='ГеоКвиз', main_page=True)


@app.route('/api/users/<user_login>')
def api_user(user_login):  # Информация о пользователе для ботов
    session = db_session.create_session()
    user = session.query(User).filter(User.login == user_login)
    return json.dumps({"name": user.name, "login": user.login, "score": user.score,
                       "solved_riddles": [found.riddle.id for found in user.founds],
                       "created_riddles": [riddle.id for riddle in user.riddles]})


@app.route('/api/user_list')
def api_user_list():  # Информация о всех пользователях для ботов
    session = db_session.create_session()
    return json.dumps([{"name": user.name, "login": user.login, "score": user.score}
                       for user in session.query(User).all()])


@app.route('/api/riddle/<riddle_id>')
def api_riddle(riddle_id):  # Информация о загадке для ботов
    session = db_session.create_session()
    riddle = session.query(Riddle).filter(Riddle.id == riddle_id)
    return json.dumps({"id": riddle.id, "pos": riddle.pos, "name": riddle.name, "desc": riddle.desc,
                       "author": riddle.author.login, "made_date": riddle.made_date})


def main():  # Основная функция - запуск базы и сервера
    db_session.global_init("db/stalker_base.sqlite")
    app.run(host="0.0.0.0")


if __name__ == '__main__':
    main()
