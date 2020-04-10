import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Riddle(SqlAlchemyBase):
    __tablename__ = "anomalies"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    pos = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    desc = sqlalchemy.Column(sqlalchemy.Text)
    ans = sqlalchemy.Column(sqlalchemy.String)
    made_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    author = orm.relation('User')

    founds = orm.relation('Found', back_populates='riddle')
    comments = orm.relation('Comment', back_populates='riddle')
