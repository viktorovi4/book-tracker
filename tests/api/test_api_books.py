import pytest
from book_tracker import create_app
from book_tracker.extensions import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_books_returns_json(client):  # Теперь client передается как аргумент
    response = client.get('/api/books')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    
    data = response.get_json()
    
    # Проверяем, что это список
    assert isinstance(data, list)
    
    # Если в БД есть книги, проверяем поля
    if data:
        first_book = data[0]
        assert 'id' in first_book
        assert 'title' in first_book
        assert 'author' in first_book
        assert 'genre' in first_book
        assert 'date_read' in first_book