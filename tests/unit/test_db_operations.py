import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from book_tracker import create_app
from book_tracker.extensions import db
from book_tracker.models import Book

@pytest.fixture
def app():
    """Фикстура приложения с изолированной БД для каждого теста"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    """Фикстура сессии с автоматическим откатом после теста"""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()

def test_create_book(app):
    """Тест создания записи в БД"""
    with app.app_context():
        book = Book(
            title="Тестовая книга",
            author="Тест Автор",
            genre="Фантастика",
            date_read=date(2023, 1, 1)
        )
        db.session.add(book)
        db.session.commit()
        
        assert book.id is not None
        assert Book.query.count() == 1

def test_read_book(app):
    """Тест чтения записи из БД"""
    with app.app_context():
        book = Book(
            title="Тестовая книга",
            author="Тест Автор",
            genre="Фантастика",
            date_read=date(2023, 1, 1)
        )
        db.session.add(book)
        db.session.commit()
        
        retrieved = Book.query.first()
        assert retrieved.title == "Тестовая книга"

def test_update_book(app):
    """Тест обновления записи в БД"""
    with app.app_context():
        book = Book(
            title="Тестовая книга",
            author="Тест Автор",
            genre="Фантастика",
            date_read=date(2023, 1, 1)
        )
        db.session.add(book)
        db.session.commit()
        
        book.title = "Обновлённая книга"
        db.session.commit()
        
        updated = Book.query.first()
        assert updated.title == "Обновлённая книга"

def test_delete_book(app):
    """Тест удаления записи из БД"""
    with app.app_context():
        book = Book(
            title="Тестовая книга",
            author="Тест Автор",
            genre="Фантастика",
            date_read=date(2023, 1, 1)
        )
        db.session.add(book)
        db.session.commit()
        
        db.session.delete(book)
        db.session.commit()
        
        assert Book.query.count() == 0

def test_transaction_rollback(app):
    """Тест отката транзакции"""
    with app.app_context():
        book = Book(
            title="Тестовая книга",
            author="Тест Автор",
            genre="Фантастика",
            date_read=date(2023, 1, 1)
        )
        db.session.add(book)
        db.session.flush()  
        
        # В рамках текущей транзакции книга должна быть видна
        assert Book.query.count() == 1
        
        # После rollback изменения не сохранятся
        db.session.rollback()
        assert Book.query.count() == 0