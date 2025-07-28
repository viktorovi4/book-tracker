from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .extensions import db


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    date_read = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, **kwargs):
        try:
            if 'date_read' in kwargs:
                if isinstance(kwargs['date_read'], str):
                    kwargs['date_read'] = date.fromisoformat(kwargs['date_read'])
        except ValueError as e:
            raise ValueError(f"Invalid date format: {kwargs['date_read']}. Use YYYY-MM-DD") from e

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Book '{self.title}'>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'date_read': self.date_read.isoformat(),
            'user_id': self.user_id
        }


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)