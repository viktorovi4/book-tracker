import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from book_tracker import create_app
from book_tracker.extensions import db
from book_tracker.models import Book


@pytest.fixture(scope='module')
def app():
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
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()

def test_book_creation(session):
    """Тест создания объекта Book"""
    book = Book(
        title="Тестовая книга",
        author="Тест Автор",
        genre="Фантастика",
        date_read=date(2023, 1, 1)
    )
    session.add(book)
    session.commit()
    
    assert book.id is not None
    assert book.title == "Тестовая книга"

def test_required_fields(session):
    """Тест обязательных полей"""
    with pytest.raises(IntegrityError):
        book = Book(title=None, author="Автор", genre="Жанр", date_read=date.today())
        session.add(book)
        session.commit()

def test_date_validation(session):
    """Тест валидации даты"""
    with pytest.raises(ValueError, match="Invalid date format"):
        # Некорректная дата (месяц 13)
        Book(
            title="Книга с плохой датой",
            author="Автор",
            genre="Жанр",
            date_read="2023-13-01"  # Неправильный месяц
        )
    
    with pytest.raises(ValueError, match="Invalid date format"):
        # Некорректный формат
        Book(
            title="Книга с плохой датой",
            author="Автор",
            genre="Жанр",
            date_read="2023/01/01"  # Неправильный формат
        )
    
    # Проверяем, что корректная дата работает
    try:
        Book(
            title="Книга с хорошей датой",
            author="Автор",
            genre="Жанр",
            date_read="2023-01-01"  # Правильный формат
        )
    except ValueError:
        pytest.fail("Valid date raised ValueError unexpectedly")