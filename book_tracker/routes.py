from flask import render_template, request, redirect, url_for, jsonify, flash
from datetime import date
from .extensions import db
from .models import Book


def init_routes(app):
    @app.route('/')
    def home():
        genre_filter = request.args.get('genre')
        author_filter = request.args.get('author')

        query = Book.query

        if genre_filter:
            query = query.filter(Book.genre == genre_filter)
        if author_filter:
            query = query.filter(Book.author == author_filter)

        books = query.all()
        return render_template('index.html', books=books)

    @app.route('/add', methods=['GET', 'POST'])
    def add_book():
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            date_read_str = request.form['date_read']
            
            try:
                date_read = date.fromisoformat(date_read_str)
                new_book = Book(
                    title=title,
                    author=author,
                    genre=genre,
                    date_read=date_read
                )
                db.session.add(new_book)
                db.session.commit()
                flash('Книга успешно добавлена!', 'success')
                return redirect(url_for('home'))
            except ValueError:
                flash('Неверный формат даты! Используйте YYYY-MM-DD', 'error')
                return render_template('add_book.html'), 400

        return render_template('add_book.html')

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit_book(id):
        book = Book.query.get_or_404(id)

        if request.method == 'POST':
            book.title = request.form['title']
            book.author = request.form['author']
            book.genre = request.form['genre']
            
            try:
                book.date_read = date.fromisoformat(request.form['date_read'])
                db.session.commit()
                flash('Книга успешно обновлена!', 'success')
                return redirect(url_for('home'))
            except ValueError:
                flash('Неверный формат даты!', 'error')
                return render_template('edit_book.html', book=book), 400

        return render_template('edit_book.html', book=book)

    @app.route('/delete/<int:id>')
    def delete_book(id):
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        flash('Книга успешно удалена!', 'success')
        return redirect(url_for('home'))

    @app.route('/delete_all')
    def delete_all_books():
        Book.query.delete()
        db.session.commit()
        flash('Все книги удалены!', 'warning')
        return redirect(url_for('home'))


    @app.route('/api/books', methods=['GET', 'POST'])
    def get_books():
        if request.method == 'POST':
            try:
                data = request.get_json()
                new_book = Book(
                    title=data['title'],
                    author=data['author'],
                    genre=data['genre'],
                    date_read=date.fromisoformat(data['date_read'])
                )
                db.session.add(new_book)
                db.session.commit()
                return jsonify(new_book.to_dict()), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 400

        books = Book.query.all()
        return jsonify([book.to_dict() for book in books])