from datetime import date
from sqlalchemy import event
from .extensions import db

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    date_read = db.Column(db.Date, nullable=False)

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
            'date_read': self.date_read.isoformat()
        }