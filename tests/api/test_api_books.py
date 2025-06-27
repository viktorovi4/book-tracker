import requests
import json


BASE_URL = "http://127.0.0.1:5000"


def test_get_books_returns_json():
    response = requests.get(f"{BASE_URL}/api/books")
    
    # Проверяем статус-код
    assert response.status_code == 200
    
    # Проверяем, что ответ в формате JSON
    assert response.headers['Content-Type'] == 'application/json'
    
    # Парсим JSON
    data = response.json()
    
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