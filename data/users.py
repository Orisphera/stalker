import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    login = sqlalchemy.Column(sqlalchemy.String, index=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    score = sqlalchemy.Column(sqlalchemy.Integer, default=lambda: 0)

    riddles = orm.relation("Riddle", back_populates="author")
    founds = orm.relation("Found", back_populates="user")
    comments = orm.relation("Comment", back_populates="author")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
