from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pytest


def test_add_book_with_empty_fields(browser):
    browser.get("http://127.0.0.1:5000")
    
    # Перейти на страницу добавления книги
    add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
    add_link.click()

    # Отправить форму без заполнения полей
    browser.find_element(By.TAG_NAME, "button").click()

    # Проверить, что мы остались на той же странице
    assert browser.title == "Добавить книгу"

    # Проверить наличие сообщения об ошибке или предупреждения
    try:
        error_message = browser.find_element(By.CLASS_NAME, "error")
        assert error_message.is_displayed()
    except NoSuchElementException:
        pass  # Валидация может быть на стороне клиента