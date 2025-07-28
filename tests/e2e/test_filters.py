# tests\e2e\test_filters.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest

# Импортируем add_test_book из основного файла e2e тестов
# Предполагается, что файл test_book_tracker_e2e.py находится в той же директории
# Убедитесь, что в этом файле функция add_test_book использует execute_script для даты и явные ожидания
from tests.e2e.test_book_tracker_e2e import add_test_book


def test_filter_books_by_genre(login_user, clear_books):
    """
    Проверяет фильтр по жанру.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Добавляем тестовые книги
    add_test_book(browser, "Книга 1", "Автор 1", "Фантастика", "2025-07-01")
    # Явно дожидаемся успеха первой книги
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    add_test_book(browser, "Книга 2", "Автор 2", "Научная фантастика", "2025-07-02")
    # Явно дожидаемся успеха второй книги
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    # 2. Переходим на главную страницу (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем загрузки списка книг
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    # 3. Применяем фильтр по жанру "Фантастика"
    # Переходим по URL с параметром фильтра (наиболее надежный способ)
    browser.get("http://localhost:5000?genre=Фантастика") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем загрузки отфильтрованного списка
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    page_source = browser.page_source

    # 4. Проверяем результаты фильтрации
    assert "Книга 1" in page_source
    assert "Автор 1" in page_source
    # Убедимся, что книга с другим жанром отсутствует
    assert "Книга 2" not in page_source
    assert "Научная фантастика" not in page_source


def test_filter_books_by_author(login_user, clear_books):
    """
    Проверяет фильтр по автору.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Добавляем тестовые книги
    add_test_book(browser, "Книга A", "Автор X", "Жанр A", "2025-07-01")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    add_test_book(browser, "Книга B", "Автор Y", "Жанр B", "2025-07-02")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    # 2. Переходим на главную страницу (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    # 3. Применяем фильтр по автору "Автор X"
    browser.get("http://localhost:5000?author=Автор+X") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем загрузки отфильтрованного списка
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    page_source = browser.page_source

    # 4. Проверяем результаты фильтрации
    assert "Книга A" in page_source
    assert "Автор X" in page_source
    # Убедимся, что книга с другим автором отсутствует
    assert "Книга B" not in page_source
    assert "Автор Y" not in page_source


def test_clear_filter(login_user, clear_books):
    """
    Проверяет сброс фильтров.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Добавляем тестовые книги
    add_test_book(browser, "Книга 1", "Автор 1", "Фантастика", "2025-07-01")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    add_test_book(browser, "Книга 2", "Автор 2", "Научная фантастика", "2025-07-02")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )

    # 2. Переходим на главную страницу (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    # 3. Применяем фильтр
    browser.get("http://localhost:5000?genre=Фантастика") # <--- ИЗМЕНЕНО С 127.0.0.1
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )
    # Проверим, что фильтр применился
    assert "Книга 1" in browser.page_source
    assert "Книга 2" not in browser.page_source

    # 4. Сбрасываем фильтр, переходя на главную без параметров
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем загрузки полного списка
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
    )

    page_source = browser.page_source

    # 5. Проверяем, что все книги снова отображаются
    assert "Книга 1" in page_source
    assert "Книга 2" in page_source
