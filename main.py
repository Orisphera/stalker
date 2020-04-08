from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo

from data import db_session
from data.anomalies import Anomaly
from data.users import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтвердите пароль', validators=[EqualTo('password')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


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
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
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


@app.route('/empty.js')
def empty_js():
    return "function onload() {}"


class AnomalyForm(FlaskForm):
    name = StringField("Название аномалии")
    desc = StringField("Описание артефакта")
    latt = StringField("Широта в градусах")
    long = StringField("Долгота в градусах")


@app.route("/new_anomaly", methods=["GET", "POST"])
def new_anomaly():
    form = AnomalyForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        anomaly = Anomaly()
        anomaly.name = form.name.data
        anomaly.desc = form.desc.data
        anomaly.pos = f'{form.long.data},{form.latt.data}'
        current_user.anomalies.append(anomaly)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('new_anomaly.html', title='Создание аномалии', form=form)


def get_marks():
    session = db_session.create_session()
    for anomaly in session.query(Anomaly).all():
        yield f"{anomaly.pos},pmw"f"tm{anomaly.id}"


@app.route('/map.js')
def map_js():
    with open('data/map.js') as f:
        return f.read().replace('<marks>', '~'.join(get_marks()))


@app.route('/to_anomaly_page.js')
def to_anomaly_page_js():
    with open('data/to_anomaly_page.js') as f:
        return f.read()


@app.route('/')
def index():
    return render_template('index.html', title='Домашняя страница')


def main():
    db_session.global_init("db/stalker_base.sqlite")
    app.run()


if __name__ == '__main__':
    main()
