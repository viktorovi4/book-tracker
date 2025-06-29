from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import date

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
        date_read_str = request.form['date_read']
        
        # Преобразуем строку в объект date
        try:
            date_read = date.fromisoformat(date_read_str)
        except ValueError:
            return "Неверный формат даты", 400        

        new_book = Book(title=title, author=author, genre=genre, date_read=date_read)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_book.html')


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'date_read': book.date_read.isoformat()
    } for book in books])


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_book(id):
    book_to_delete = Book.query.get_or_404(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form['genre']
        date_read_str = request.form['date_read']

        try:
            book.date_read = date.fromisoformat(date_read_str)
        except ValueError:
            return "Неверный формат даты", 400

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit_book.html', book=book)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)