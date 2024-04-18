import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class SupportMessage(SqlAlchemyBase):
    __tablename__ = 'support_message'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.NVARCHAR, nullable=False)
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    message = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now().replace(microsecond=0))