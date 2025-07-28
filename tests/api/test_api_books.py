import pytest
from book_tracker import create_app
from book_tracker.extensions import db
from book_tracker.models import User


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Проверяем, существует ли пользователь, и создаем его, если нет
            if not User.query.filter_by(username="testuser").first():            

                # Добавляем тестового пользователя
                test_user = User(username="testuser")
                test_user.set_password("password")
                db.session.add(test_user)
                db.session.commit()

        yield client
        # db.drop_all() # Опционально

    with app.app_context():
        db.drop_all()


def test_get_books_returns_json(client):
    """GET /api/books — получение списка книг в формате JSON"""
    # Вход
    client.post('/login', data={'username': 'testuser', 'password': 'password'})

    # Запрос
    response = client.get('/api/books')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    data = response.get_json()
    assert isinstance(data, list)

    # Если есть данные, проверяем структуру
    if data:
        first_book = data[0]
        assert 'id' in first_book
        assert 'title' in first_book
        assert 'author' in first_book
        assert 'genre' in first_book
        assert 'date_read' in first_book


def test_api_returns_404_for_nonexistent_book(client):
    """Проверяет, что при запросе несуществующей книги возвращается 404"""
    # Вход
    client.post('/login', data={'username': 'testuser', 'password': 'password'})

    response = client.get('/api/books/99999')
    assert response.status_code == 404


def test_add_book_via_api(client):
    """POST /api/books — добавление новой книги через API"""
    # Вход
    client.post('/login', data={'username': 'testuser', 'password': 'password'})

    new_book_data = {
        "title": "API Книга",
        "author": "API Автор",
        "genre": "Фантастика",
        "date_read": "2025-06-28"
    }

    response = client.post('/api/books', json=new_book_data)
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'

    data = response.get_json()
    assert data['title'] == new_book_data['title']
    assert data['author'] == new_book_data['author']
    assert data['genre'] == new_book_data['genre']
    assert data['date_read'] == new_book_data['date_read']


def test_update_book_via_api(client):
    """PUT /api/books/<id> — обновление существующей книги"""
    # Вход
    client.post('/login', data={'username': 'testuser', 'password': 'password'})

    # Сначала добавляем книгу через API
    add_response = client.post('/api/books', json={
        "title": "Книга для редактирования",
        "author": "Автор",
        "genre": "Драма",
        "date_read": "2025-06-28"
    })
    assert add_response.status_code == 201
    book_id = add_response.get_json()['id']

    # Обновляем её через API
    updated_data = {
        "title": "Обновлённая книга",
        "author": "Новый автор",
        "genre": "Научная фантастика",
        "date_read": "2025-07-01"
    }

    response = client.put(f'/api/books/{book_id}', json=updated_data)
    assert response.status_code == 200

    data = response.get_json()
    assert data['title'] == updated_data['title']
    assert data['author'] == updated_data['author']
    assert data['genre'] == updated_data['genre']
    assert data['date_read'] == updated_data['date_read']


def test_delete_book_via_api(client):
    """DELETE /api/books/<id> — удаление книги по ID"""
    # Вход
    client.post('/login', data={'username': 'testuser', 'password': 'password'})

    # Сначала добавляем книгу через API
    add_response = client.post('/api/books', json={
        "title": "Книга для удаления",
        "author": "Тестовый Автор",
        "genre": "Боевик",
        "date_read": "2025-06-28"
    })
    assert add_response.status_code == 201
    book_id = add_response.get_json()['id']

    # Удаляем её через API
    delete_response = client.delete(f'/api/books/{book_id}')
    assert delete_response.status_code == 200

    data = delete_response.get_json()
    assert data['message'] == f'Книга с ID {book_id} успешно удалена'

    # Проверяем, что книга больше не существует
    get_response = client.get(f'/api/books/{book_id}')
    assert get_response.status_code == 404