from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import tempfile
import shutil
import json


@pytest.fixture
def browser():
    # Создаём временную директорию для профиля Chrome
    temp_dir = tempfile.mkdtemp()
    # Настройки браузера
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Запуск без GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")  # Уникальная директория
    # Инициализируем драйвер
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    # Чистка после теста
    driver.quit()
    shutil.rmtree(temp_dir)


def get_books_api(browser):
    """Получает список книг через API /api/books"""
    browser.get("http://127.0.0.1:5000/api/books")
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body_text = browser.find_element(By.TAG_NAME, "body").text
        return json.loads(body_text)
    except Exception as e:
        print("Ошибка при получении /api/books:", str(e))
        print("Текущий HTML:\n", browser.page_source)
        raise


def test_edit_book(browser):
    """
    Тест: редактирование книги и проверка изменений на главной странице
    """

    # Открытие главной страницы
    browser.get("http://127.0.0.1:5000")

    # Если книг нет, добавляем тестовую
    if "Пока нет ни одной книги." in browser.page_source:
        add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
        add_link.click()

        browser.find_element(By.NAME, "title").send_keys("Книга для редактирования")
        browser.find_element(By.NAME, "author").send_keys("Старый Автор")
        browser.find_element(By.NAME, "genre").send_keys("Фантастика")
        browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-26'")
        browser.find_element(By.TAG_NAME, "button").click()

        # Ждём появления книги на главной
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Книга для редактирования")
        )

    # Кликаем по ссылке "Редактировать"
    try:
        edit_link = browser.find_element(By.LINK_TEXT, "✏️ Редактировать")
        edit_link.click()
    except NoSuchElementException:
        print("Ссылка 'Редактировать' не найдена.")
        print("Текущий URL:", browser.current_url)
        print("HTML страницы:\n", browser.page_source)
        raise

    # Изменяем данные формы
    title_input = browser.find_element(By.NAME, "title")
    title_input.clear()
    title_input.send_keys("Обновлённая книга")

    author_input = browser.find_element(By.NAME, "author")
    author_input.clear()
    author_input.send_keys("Новый Автор")

    genre_input = browser.find_element(By.NAME, "genre")
    genre_input.clear()
    genre_input.send_keys("Научная фантастика")

    # Установка даты через JavaScript
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-07-01'")

    # Сохраняем изменения
    save_button = browser.find_element(By.XPATH, '//button[text()="Сохранить изменения"]')
    save_button.click()

    # Возвращаемся на главную
    browser.get("http://127.0.0.1:5000")

    # Явное ожидание появления обновлённой книги
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Обновлённая книга")
        )
    except TimeoutException:
        print("Ошибка: Обновлённая книга не отобразилась за 10 секунд.")
        print("Текущий URL:", browser.current_url)
        print("Исходный HTML:\n", browser.page_source)
        raise

    # Найти элемент с обновлённой книгой по заголовку
    updated_book_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//li[contains(., "Обновлённая книга")]'))
    )
    book_text = updated_book_element.text
    print("Текст элемента:", book_text)
    
    # Проверяем наличие новых данных
    assert "Обновлённая книга" in book_text
    assert "новый автор" in book_text.lower(), f"Expected 'новый автор' in {book_text}"
    assert "Научная фантастика" in book_text

    # Проверяем отсутствие старых данных
    assert "Книга для редактирования" not in book_text
    assert "Старый Автор" not in book_text
    assert "Фантастика" not in book_text

    # Проверка через API (необязательно, но полезно для дебага)
    books = get_books_api(browser)
    first_book = books[0]

    assert first_book["title"] == "Обновлённая книга"
    assert first_book["author"] == "Новый Автор"
    assert first_book["genre"] == "Научная фантастика"
    assert first_book["date_read"] == "2025-07-01"