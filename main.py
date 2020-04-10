from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
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


@app.route('/empty.js')
def empty_js():
    return "function onload() {}"


class NewAnomalyForm(FlaskForm):
    latt_deg = StringField("", validators=[DataRequired()])
    latt_min = StringField("", validators=[DataRequired()])
    latt_sec = StringField("", validators=[DataRequired()])
    long_deg = StringField("", validators=[DataRequired()])
    long_min = StringField("", validators=[DataRequired()])
    long_sec = StringField("", validators=[DataRequired()])
    name = StringField("Название аномалии:", validators=[DataRequired()])
    desc = StringField("Описание артефакта:", validators=[DataRequired()])
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField('Создать')


@app.route("/new_anomaly.js")
def new_anomaly_js():
    with open("data/new_anomaly.js") as f:
        return f.read()


@app.route("/new_anomaly", methods=["GET", "POST"])
def new_anomaly():
    form = NewAnomalyForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        riddle = Riddle()
        long = float(form.long_deg.data) + (
                    float(form.long_min.data) + float(form.long_sec.data) / 60) / 60
        latt = float(form.latt_deg.data) + (
                    float(form.latt_min.data) + float(form.latt_sec.data) / 60) / 60
        riddle.pos = f'{long},{latt}'
        riddle.name = form.name.data
        riddle.desc = form.desc.data
        riddle.ans = form.ans.data
        current_user.anomalies.append(riddle)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('new_anomaly.html', form=form)


def get_marks():
    session = db_session.create_session()
    for riddle in session.query(Riddle).all():
        found = current_user.is_authenticated and session.query(Found)\
            .filter((Found.user_id == current_user.id) & (Found.anomaly_id == riddle.id))
        yield f"{riddle.pos},pm{'gr' if found else 'wt'}m{riddle.id}"


@app.route('/map.js')
def map_js():
    with open('data/map.js') as f:
        return f.read().replace('<marks>', '~'.join(get_marks()))


@app.route('/anomaly_on_map.js')
def anomaly_on_map_js():
    with open('data/anomaly_on_map.js') as f:
        return f.read()


@app.route('/to_page.js')
def to_anomaly_page_js():
    with open('data/to_page.js') as f:
        return f.read()


@app.route("/riddle.js")
def anomaly_js():
    with open("data/riddle.js") as f:
        return f.read()


class AnomalyAnswerForm(FlaskForm):
    ans = StringField("Ответ:", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route('/anomalies/<int:anomaly_id>', methods=["GET", "POST"])
def anomaly_page(anomaly_id):
    session = db_session.create_session()
    riddle = session.query(Riddle).filter(Riddle.id == anomaly_id).one()
    form = AnomalyAnswerForm()
    if form.validate_on_submit():
        if form.ans.data == riddle.ans:
            message = "Правильно!"
            if current_user.is_authenticated and \
               not session.query(Found).filter((Found.user_id == current_user.id) &
                                               (Found.anomaly_id == anomaly_id)).all():
                new_found = Found()
                new_found.user_id = current_user.id
                new_found.anomaly_id = anomaly_id
                current_user.founds.append(new_found)
                current_user.score += 5
                print(current_user.score)
                session.merge(current_user)
                session.commit()
        else:
            message = "Неправильный ответ"
        return render_template('riddle.html', riddle=riddle, form=form, message=message)
    return render_template('riddle.html', riddle=riddle, form=form)


@app.route('/users/<user_login>')
def user_page(user_login):
    session = db_session.create_session()
    user = session.query(User).filter(User.login == user_login).one()
    return render_template('user.html', user=user)


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
    return render_template('index.html', title='Домашняя страница')


def main():
    db_session.global_init("db/stalker_base.sqlite")
    app.run()


if __name__ == '__main__':
    main()
