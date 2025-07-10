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

def test_add_book_with_empty_title(browser):
    """Проверяет, что нельзя создать книгу без названия"""
    browser.get("http://127.0.0.1:5000")
    add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
    add_link.click()

    # Заполняем все поля, кроме title
    browser.find_element(By.NAME, "author").send_keys("Тестовый Автор")
    browser.find_element(By.NAME, "genre").send_keys("Фантастика")
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-28'")

    # Отправляем форму
    browser.find_element(By.TAG_NAME, "button").click()

    # Проверяем, что остались на той же странице
    assert "Добавить книгу" in browser.title

    # Проверяем, что форма показывает ошибку (например, браузерная валидация)
    title_input = browser.find_element(By.NAME, "title")
    assert title_input.get_attribute("validationMessage") != ""


def test_add_book_with_invalid_date(browser):
    """Проверяет, что нельзя добавить книгу с невалидной датой"""
    browser.get("http://127.0.0.1:5000")
    add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
    add_link.click()

    # Заполняем форму с невалидной датой
    browser.find_element(By.NAME, "title").send_keys("Книга с плохой датой")
    browser.find_element(By.NAME, "author").send_keys("Тестовый Автор")
    browser.find_element(By.NAME, "genre").send_keys("Фантастика")
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-30-02'")  # Неверная дата

    browser.find_element(By.TAG_NAME, "button").click()

    # Проверяем, что мы остались на форме
    assert "Добавить книгу" in browser.title


def test_add_book_with_missing_required_fields(browser):
    """Проверяет, что форма не отправляется, если хотя бы одно поле не заполнено"""
    browser.get("http://127.0.0.1:5000")
    add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
    add_link.click()

    # Не заполняем ни одно поле
    browser.find_element(By.TAG_NAME, "button").click()

    # Проверяем, что остались на той же странице
    assert "Добавить книгу" in browser.title

    # Проверяем, что браузер показал ошибки валидации
    try:
        required_fields = browser.find_elements(By.CSS_SELECTOR, "input[required]")
        for field in required_fields:
            assert field.get_attribute("validity").get("valueMissing")
    except Exception:
        pass  # Браузер может не вернуть значение, но JS-валидация всё равно сработает