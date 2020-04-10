import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Found(SqlAlchemyBase):
    __tablename__ = 'found'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')

    riddle_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('anomalies.id'))
    riddle = orm.relation('Riddle')

    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
