from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest


def test_delete_book(browser):
    # Переходим на главную
    browser.get("http://127.0.0.1:5000")

    # Если нет книг — сначала добавим одну
    if "Пока нет ни одной книги." in browser.page_source:
        add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить новую книгу")
        add_link.click()
        browser.find_element(By.NAME, "title").send_keys("Книга для удаления")
        browser.find_element(By.NAME, "author").send_keys("Тестовый Автор")
        browser.find_element(By.NAME, "genre").send_keys("Фантастика")
        browser.find_element(By.NAME, "date_read").send_keys("2025-06-26")
        browser.find_element(By.TAG_NAME, "button").click()
        browser.get("http://127.0.0.1:5000")

    # Ждём появления ссылки "Удалить"
    try:
        delete_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Удалить"))
        )
        delete_button.click()
    except:
        # Если "Удалить" не найден, попробуем найти с эмодзи
        delete_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "🗑️ Удалить"))
        )
        delete_button.click()

    # Проверяем, что книга исчезла
    WebDriverWait(browser, 10).until_not(
        EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Книга для удаления")
    )

    assert "Книга для удаления" not in browser.page_source