import random

from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import orm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo

from data import db_session
from data.riddles import Riddle
from data.found import Found
from data.users import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/empty.js')
def empty_js():
    return "function onl""oad() {}"


def get_marks():
    session = db_session.create_session()
    for riddle in session.query(Riddle).all():
        found = current_user.is_authenticated and session.query(Found)\
            .filter((Found.user_id == current_user.id) & (Found.riddle_id == riddle.id))
        yield f"{riddle.pos},pm{'gr' if found else 'wt'}m{riddle.id}"


@app.route('/map.js')
def map_js():
    session = db_session.create_session()
    try:
        riddle = random.choice(tuple(session.query(Riddle).all()))
        long, latt = riddle.pos.split(',')
    except IndexError:
        long = latt = 0
    with open('data/map.js') as f:
        return (f.read().replace('<marks>', '~'.join(get_marks()))
                .replace('<long>', long).replace('<latt>', latt))


@app.route('/to_page.js')
def to_riddle_page_js():
    with open('data/to_page.js') as f:
        return f.read()


@app.route('/riddle_on_map.js')
def riddle_on_map_js():
    with open('data/riddle_on_map.js') as f:
        return f.read()


@app.route('/riddle_on_map1.js')
def riddle_on_map1js():
    with open('data/riddle_on_map1.js') as f:
        return f.read()


@app.route("/new_riddle.js")
def new_riddle_js():
    with open("data/new_riddle.js") as f:
        return f.read()


@app.route("/riddle.js")
def riddle_js():
    with open("data/riddle.js") as f:
        return f.read()


class RegisterForm(FlaskForm):
    name = StringField('Имя:', validators=[DataRequired()])
    login = StringField('Логин:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password2 = PasswordField('Подтвердите пароль:', validators=[EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        return redirect('/')
    return render_template('register.html', title="Регистрация", form=form)


class LoginForm(FlaskForm):
    login = StringField('Логин:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
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
def logout():
    logout_user()
    return redirect("/")


def update_riddle_from_form(form, riddle):
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
def new_riddle():
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
        return redirect('/')
    return render_template('edit_riddle.html', form=form, is_new=True, title="Создание загадки")


class RiddleAnswerForm(FlaskForm):
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route('/riddles/<int:riddle_id>', methods=["GET", "POST"])
def riddle_page(riddle_id):
    session = db_session.create_session()
    try:
        riddle = session.query(Riddle).filter(Riddle.id == riddle_id).one()
    except orm.exc.NoResultFound:
        return render_template('missing_riddle.html', title='Такой загадки нет')
    form = RiddleAnswerForm()
    if form.validate_on_submit():
        if form.ans.data == riddle.ans:
            message = "Правильно!"
            if current_user.is_authenticated and \
               not session.query(Found).filter((Found.user_id == current_user.id) &
                                               (Found.riddle_id == riddle_id)).all():
                new_found = Found()
                new_found.user_id = current_user.id
                new_found.riddle_id = riddle_id
                current_user.founds.append(new_found)
                current_user.score += 5
                session.merge(current_user)
                session.commit()
        else:
            message = "Неправильный ответ"
            if current_user.is_authenticated:
                current_user.score -= 3
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
def edit_riddle(riddle_id):
    session = db_session.create_session()
    try:
        riddle = session.query(Riddle).filter(Riddle.id == riddle_id).one()
    except orm.exc.NoResultFound:
        return render_template('missing_riddle.html', title='Такой загадки нет')
    form = RiddleEditForm()
    if form.validate_on_submit():
        try:
            update_riddle_from_form(form, riddle)
        except ValueError:
            return render_template('edit_riddle.html', form=form, title="Редактирование загадки",
                                   can_edit=(current_user.is_authenticated and
                                             current_user.id == riddle.author_id),
                                   message="Неверный формат координат")
        session.merge(riddle)
        session.commit()
        return redirect(f'/riddles/{riddle_id}')
    form.long_deg.default, form.latt_deg.default = riddle.pos.split(',')
    form.name.default = riddle.name
    form.desc.default = riddle.desc
    form.ans.default = riddle.ans
    form.process()
    return render_template('edit_riddle.html', form=form, title="Редактирование загадки",
                           can_edit=(current_user.is_authenticated and
                                     current_user.id == riddle.author_id))


@app.route('/users/<user_login>')
def user_page(user_login):
    session = db_session.create_session()
    try:
        user = session.query(User).filter(User.login == user_login).one()
        return render_template('user.html', user=user, title=f"Страница пользователя {user.name}")
    except orm.exc.NoResultFound:
        return render_template('missing_user.html', title="Страница несуществующего пользователя")


@app.route('/score-table')
def score_table():
    session = db_session.create_session()
    users = session.query(User).order_by(User.score.desc())
    return render_template('score_table.html', users=users, title="Положение")


@app.route('/help')
def help1():
    return render_template('help.html', title="Как играть")


@app.route('/')
def index():
    return render_template('index.html', title='Домашняя страница', main_page=True)


def main():
    db_session.global_init("db/stalker_base.sqlite")
    app.run(host="0.0.0.0")


if __name__ == '__main__':
    main()
