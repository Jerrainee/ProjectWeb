import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    data = sqlalchemy.Column(sqlalchemy.JSON, nullable=False)
    results = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comments = orm.relationship('Comments')