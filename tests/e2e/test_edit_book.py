from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import tempfile
import shutil
import time


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


def test_edit_book(browser):
    """
    Тест: редактирование книги и проверка изменений на главной странице
    """

    # Открытие главной страницы
    browser.get("http://127.0.0.1:5000")

    # Если книг нет, добавляем тестовую вручную (как в test_add_book)
    if "Пока нет ни одной книги." in browser.page_source:
        add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
        add_link.click()

        browser.find_element(By.NAME, "title").send_keys("Книга для редактирования")
        browser.find_element(By.NAME, "author").send_keys("Старый Автор")
        browser.find_element(By.NAME, "genre").send_keys("Фантастика")
        browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-26'")
        browser.find_element(By.TAG_NAME, "button").click()
        time.sleep(1)  # Небольшая пауза, чтобы данные точно сохранились
        browser.get("http://127.0.0.1:5000")

    # Кликаем по ссылке "Редактировать"
    try:
        edit_link = browser.find_element(By.LINK_TEXT, "✏️ Редактировать")
        edit_link.click()
    except Exception as e:
        print("Ошибка при переходе к редактированию:", str(e))
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

    # Установка даты через JavaScript (надёжнее)
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-07-01'")

    # Сохраняем изменения
    save_button = browser.find_element(By.XPATH, '//button[text()="Сохранить изменения"]')
    save_button.click()

    # Возвращаемся на главную
    browser.get("http://127.0.0.1:5000")

    # Ждём появления обновлённой книги
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Обновлённая книга")
        )
    except TimeoutException:
        print("Ошибка: Обновлённая книга не отобразилась за 10 секунд.")
        print("Текущий URL:", browser.current_url)
        print("Исходный HTML:\n", browser.page_source)
        raise

    # Проверяем, что старое название исчезло, а новое присутствует
    page_source = browser.page_source
    assert "Обновлённая книга" in page_source
    assert "Книга для редактирования" not in page_source
    assert "Старый Автор" not in page_source
    assert "Фантастика" not in page_source