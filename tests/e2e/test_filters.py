from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest
import requests


@pytest.fixture
def clear_books():
    """Фикстура для очистки всех книг перед тестом"""
    def _clear_books():
        response = requests.get("http://127.0.0.1:5000/delete_all")
        if response.status_code != 200:
            raise Exception("Не удалось очистить книги")
    return _clear_books


def add_test_books(browser):
    """Вспомогательная функция для добавления тестовых книг"""
    # Добавляем первую книгу
    browser.get("http://127.0.0.1:5000/add")
    browser.find_element(By.NAME, "title").send_keys("Книга 1")
    browser.find_element(By.NAME, "author").send_keys("Автор 1")
    browser.find_element(By.NAME, "genre").send_keys("Фантастика")
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-28'")
    browser.find_element(By.TAG_NAME, "button").click()

    # Добавляем вторую книгу
    browser.get("http://127.0.0.1:5000/add")
    browser.find_element(By.NAME, "title").send_keys("Книга 2")
    browser.find_element(By.NAME, "author").send_keys("Автор 2")
    browser.find_element(By.NAME, "genre").send_keys("Научная фантастика")
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-29'")
    browser.find_element(By.TAG_NAME, "button").click()


def wait_for_page_load(browser, timeout=10):
    """Ожидание загрузки страницы"""
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        print("Ошибка: Страница не загрузилась за", timeout, "секунд.")
        print("Текущий URL:", browser.current_url)
        print("HTML:\n", browser.page_source)
        raise


def test_filter_books_by_genre(clear_books, browser):
    """
    Проверяет фильтрацию по жанру (?genre=...)
    """
    # Очищаем и добавляем тестовые данные
    clear_books()
    add_test_books(browser)

    # Применяем фильтр
    browser.get("http://127.0.0.1:5000?genre=Фантастика")
    wait_for_page_load(browser)

    page_source = browser.page_source

    # Проверяем результаты фильтрации
    assert "Книга 1" in page_source, "Книга с нужным жанром должна отображаться"
    assert "Автор 1" in page_source, "Автор книги с нужным жанром должен отображаться"
    assert "Фантастика" in page_source, "Нужный жанр должен отображаться"
    
    # Проверяем, что книги с другим жанром не отображаются
    assert "Книга 2" not in page_source, "Книга с другим жанром не должна отображаться"
    assert "Научная фантастика" not in page_source, "Другой жанр не должен отображаться"


def test_filter_books_by_author(clear_books, browser):
    """
    Проверяет фильтрацию по автору (?author=...)
    """
    # Очищаем и добавляем тестовые данные
    clear_books()
    add_test_books(browser)

    # Применяем фильтр
    browser.get("http://127.0.0.1:5000?author=Автор 1")
    wait_for_page_load(browser)

    page_source = browser.page_source

    # Проверяем результаты фильтрации
    assert "Книга 1" in page_source, "Книга нужного автора должна отображаться"
    assert "Автор 1" in page_source, "Нужный автор должен отображаться"
    assert "Фантастика" in page_source, "Жанр книги нужного автора должен отображаться"
    
    # Проверяем, что книги других авторов не отображаются
    assert "Книга 2" not in page_source, "Книга другого автора не должна отображаться"
    assert "Автор 2" not in page_source, "Другой автор не должен отображаться"


def test_clear_filter(clear_books, browser):
    """
    Проверяет сброс фильтров
    """
    # Очищаем и добавляем тестовые данные
    clear_books()
    add_test_books(browser)

    # Сначала применяем фильтр
    browser.get("http://127.0.0.1:5000?genre=Фантастика")
    wait_for_page_load(browser)

    # Затем сбрасываем фильтр
    browser.get("http://127.0.0.1:5000")
    wait_for_page_load(browser)

    page_source = browser.page_source

    # Проверяем, что все книги отображаются
    assert "Книга 1" in page_source, "Все книги должны отображаться после сброса фильтра"
    assert "Книга 2" in page_source, "Все книги должны отображаться после сброса фильтра"
    assert "Автор 1" in page_source, "Все авторы должны отображаться после сброса фильтра"
    assert "Автор 2" in page_source, "Все авторы должны отображаться после сброса фильтра"