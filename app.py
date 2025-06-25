from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    date_read = db.Column(db.Date, nullable=False)


@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        date_read = request.form['date_read']

        new_book = Book(title=title, author=author, genre=genre, date_read=date_read)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_book.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)