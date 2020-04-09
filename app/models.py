from app import db
from datetime import datetime

class User(db.Model):

    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.email

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated


class Event(db.Model):

    __tablename__ = 'event'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author = db.Column(db.ForeignKey('user.email'))
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    title = db.Column(db.String(length=30), unique=False, nullable=False)
    desc = db.Column(db.String, unique=False, nullable=False)
