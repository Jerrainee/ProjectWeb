import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class ForumPost(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    messages = orm.relationship("Message")
    author = orm.relationship('User', overlaps="posts")
