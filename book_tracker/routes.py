from flask import render_template, request, redirect, url_for, jsonify, flash, abort
from datetime import date, datetime
from .extensions import db
from .models import Book, User
from collections import defaultdict
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegistrationForm, LoginForm

def init_routes(app):
    @app.route('/')
    def home():
        if not current_user.is_authenticated:
            flash("Пожалуйста, войдите в систему, чтобы увидеть свои книги", "info")
            return redirect(url_for('login'))

        query = Book.query.filter_by(user_id=current_user.id)

        genre_filter = request.args.get('genre')
        author_filter = request.args.get('author')

        if genre_filter:
            query = query.filter(Book.genre == genre_filter)
        if author_filter:
            query = query.filter(Book.author == author_filter)

        books = query.all()

        # Подготовка данных для графика
        monthly_stats = defaultdict(int)
        for book in books:
            month_key = book.date_read.strftime("%Y-%m")
            monthly_stats[month_key] += 1

        chart_labels = []
        chart_data = []
        for month in sorted(monthly_stats.keys()):
            chart_labels.append(datetime.strptime(month, "%Y-%m").strftime("%b %Y"))
            chart_data.append(monthly_stats[month])

        return render_template(
            'index.html',
            books=books,
            chart_labels=chart_labels,
            chart_data=chart_data
        )

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_book():
        if request.method == 'POST':
            # Используем .get с пустой строкой по умолчанию для избежания KeyError
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            genre = request.form.get('genre', '').strip()
            # === ИСПРАВЛЕНИЕ ===
            # Получаем дату как строку, используя .get(), чтобы избежать KeyError
            # request.form['date_read'] может вызвать KeyError, если ключ отсутствует
            date_read_str = request.form.get('date_read', '').strip()
            # ===============

            # Проверка обязательных полей (включая дату)
            if not title:
                flash('Название книги обязательно.', 'error')
                return render_template('add_book.html'), 400
            if not author:
                flash('Автор обязателен.', 'error')
                return render_template('add_book.html'), 400
            if not genre:
                flash('Жанр обязателен.', 'error')
                return render_template('add_book.html'), 400
            # === ИСПРАВЛЕНИЕ ===
            # Проверяем, что дата была введена (не пустая строка)
            if not date_read_str:
                flash('Дата прочтения обязательна.', 'error')
                return render_template('add_book.html'), 400
            # ===============

            try:
                # Пытаемся преобразовать дату
                # Теперь date_read_str гарантированно является строкой
                #date_read = date.fromisoformat(date_read_str)
                date_read = date.fromisoformat(request.form.get('date_read', ''))
                # Создание и сохранение книги
                new_book = Book(title=title,
                            author=author,
                            genre=genre,
                            date_read=date_read,
                            user_id=current_user.id)
                db.session.add(new_book)
                db.session.commit()
                flash('Книга успешно добавлена!', 'success')
                return redirect(url_for('home'))
            # === ИСПРАВЛЕНИЕ ===
            # Ловим конкретно ValueError, которое возникает при неверном формате даты
            except ValueError as e:
                # print(f"Debug: Ошибка валидации даты: {e}") # Для отладки на сервере
                flash('Неверный формат даты! Используйте YYYY-MM-DD', 'error')
                return render_template('add_book.html', 
                                    title=request.form.get('title'),
                                    author=request.form.get('author'),
                                    genre=request.form.get('genre'),
                                    date_read=request.form.get('date_read')), 400 # Возвращаем ту же страницу с кодом 400
            # ===============
        # Для GET-запроса просто отображаем форму
        return render_template('add_book.html')

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_book(id):
        book = db.session.get(Book, id)
        if not book:
            abort(404)
        if book.user_id != current_user.id:
            flash("Вы не можете редактировать чужие книги", "error")
            return redirect(url_for('home'))

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
    @login_required
    def delete_book(id):
        book = db.session.get(Book, id)
        if not book:
            abort(404)
        if book.user_id != current_user.id:
            flash("Вы не можете удалять чужие книги", "error")
            return redirect(url_for('home'))

        db.session.delete(book)
        db.session.commit()
        flash('Книга успешно удалена!', 'success')
        return redirect(url_for('home'))

    @app.route('/delete_all')
    @login_required    
    def delete_all_books():
        Book.query.delete()
        db.session.commit()
        flash('Все книги удалены!', 'warning')
        return redirect(url_for('home'))

    @app.route('/api/books/<int:id>', methods=['GET'])
    @login_required
    def get_book(id):
        book = db.session.get(Book, id)
        if not book:
            return jsonify({"error": "Книга не найдена"}), 404
        return jsonify(book.to_dict())

    @app.route('/api/books', methods=['GET', 'POST'])
    @login_required
    def get_books():
        if request.method == 'POST':
            try:
                data = request.get_json()
                new_book = Book(
                    title=data['title'],
                    author=data['author'],
                    genre=data['genre'],
                    date_read=date.fromisoformat(data['date_read']),
                    user_id=current_user.id
                )
                db.session.add(new_book)
                db.session.commit()
                return jsonify(new_book.to_dict()), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 400

        books = Book.query.filter_by(user_id=current_user.id).all()
        return jsonify([book.to_dict() for book in books])
    
    @app.route('/api/books/<int:id>', methods=['PUT'])
    def update_book(id):
        book = db.session.get(Book, id)
        if not book:
            abort(404)
        data = request.get_json()

        try:
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.genre = data.get('genre', book.genre)
            if 'date_read' in data:
                book.date_read = date.fromisoformat(data['date_read'])

            db.session.commit()
            return jsonify(book.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
        
    @app.route('/api/books/<int:id>', methods=['DELETE'])
    def delete_api_book(id):
        book = db.session.get(Book, id)
        if not book:
            abort(404)
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": f"Книга с ID {id} успешно удалена"}), 200
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash("Этот логин уже занят", "error")
                return render_template('register.html', form=form)
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Вы успешно зарегистрированы!", "success")
            return redirect(url_for('login'))
        return render_template('register.html', form=form)


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Неверный логин или пароль", "error")
                return redirect(url_for('login'))
            login_user(user)
            flash("Вы вошли в систему", "success")
            return redirect(url_for('home'))
        return render_template('login.html', form=form)


    @app.route('/logout')
    def logout():
        logout_user()
        flash("Вы вышли из системы", "success")
        return redirect(url_for('home'))