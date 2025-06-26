from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pytest


@pytest.fixture
def browser():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()


def test_add_book(browser):
    # Открыть главную страницу
    browser.get("http://127.0.0.1:5000")

    # Перейти на страницу добавления книги
    add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
    add_link.click()

    # Заполнить форму
    browser.find_element(By.NAME, "title").send_keys("Тестовая книга")
    browser.find_element(By.NAME, "author").send_keys("Тестовый Автор")
    browser.find_element(By.NAME, "genre").send_keys("Фантастика")
    browser.find_element(By.NAME, "date_read").send_keys("26-06-2025")

    # Отправить форму
    browser.find_element(By.TAG_NAME, "button").click()

    # Ждать появления текста книги
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Тестовая книга")
    )

    # Проверить, что книга отображается
    assert "Тестовая книга" in browser.page_source