# tests\e2e\test_negative_scenarios.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest


def test_add_book_with_empty_fields(login_user, clear_books):
    """
    Проверяет, что книга не добавляется, если обязательные поля пусты.
    Поскольку поля имеют атрибут 'required', браузер может блокировать отправку.
    Мы обходим это, удаляя атрибут 'required' через JS перед отправкой.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Переходим на страницу добавления (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000/add")

    # Явно ждем загрузки формы
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.book-form")))

    # === КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ ===
    # 2. Удаляем атрибут 'required' со всех полей ввода, чтобы обойти валидацию браузера
    try:
        required_inputs = browser.find_elements(By.CSS_SELECTOR, "form.book-form input[required]")
        for input_elem in required_inputs:
            browser.execute_script("arguments[0].removeAttribute('required');", input_elem)
    except Exception:
        pass # Продолжаем даже если не удалось
    # =============================

    # 3. Нажимаем кнопку отправки (пустая форма)
    submit_button = browser.find_element(By.CSS_SELECTOR, "form.book-form button[type='submit']")
    submit_button.click()

    # === КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ ===
    # 4. Ждем и проверяем наличие сообщения об ошибке от сервера
    # Явно ждем, пока элемент не только появится, но и станет видимым
    try:
        error_message_element = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-error"))
        )
        # Проверяем, что сообщение об ошибке не пустое
        error_text = error_message_element.text.strip()
        assert len(error_text) > 0, "Сообщение об ошибке пустое"
        
    except TimeoutException:
        # Если сообщение об ошибке не появилось, это ошибка теста
        current_url = browser.current_url
        page_source_snippet = browser.page_source[:1000]
        raise AssertionError(
            f"Сообщение об ошибке не появилось после отправки формы с пустыми полями (после удаления 'required'). "
            f"Текущий URL: {current_url}. Фрагмент страницы: {page_source_snippet}"
        )
    # =============================


def test_add_book_with_invalid_date(login_user, clean_db):
    """Проверяет, что книга не добавляется, если дата в неверном формате."""
    browser = login_user
    
    # 1. Переходим на страницу добавления
    browser.get("http://localhost:5000/add")
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.book-form")))
    
    # 2. Заполняем обязательные поля
    browser.execute_script("""
        document.querySelector('[name="title"]').value = 'Книга с неверной датой';
        document.querySelector('[name="author"]').value = 'Автор';
        document.querySelector('[name="genre"]').value = 'Жанр';
    """)
    
    # 3. Устанавливаем пустое значение для даты (чтобы обойти HTML5 валидацию)
    date_field = browser.find_element(By.NAME, "date_read")
    browser.execute_script("arguments[0].value = '';", date_field)
    
    # 4. Отправляем форму с невалидными данными через POST-запрос (минуя браузерную валидацию)
    browser.execute_script("""
        const form = document.querySelector('form.book-form');
        const formData = new FormData(form);
        formData.set('date_read', 'неправильная-дата');
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'text/html',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            document.documentElement.innerHTML = html;
        });
    """)
    
    # 5. Ждем обновления страницы и проверяем сообщение об ошибке
    try:
        error_element = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-error")))
        error_text = error_element.text
        
        assert "Неверный формат даты" in error_text or "YYYY-MM-DD" in error_text, \
            f"Ожидалось сообщение о неверном формате даты, получено: '{error_text}'"
    except TimeoutException:
        current_url = browser.current_url
        page_source = browser.page_source[:2000]
        raise AssertionError(
            f"Сообщение об ошибке не появилось. URL: {current_url}\n"
            f"Фрагмент страницы:\n{page_source}"
        )
    
    # 6. Проверяем, что остались на странице добавления
    assert browser.current_url == "http://localhost:5000/add", \
        f"После ошибки должны остаться на странице добавления, текущий URL: {browser.current_url}"
    
    # 7. Проверяем, что книга не добавилась
    browser.get("http://localhost:5000")
    assert "Книга с неверной датой" not in browser.page_source, \
        "Книга с неверной датой не должна была добавиться в список"

