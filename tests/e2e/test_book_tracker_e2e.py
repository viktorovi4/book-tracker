# tests/e2e/test_book_tracker_e2e.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest

def add_test_book(browser, title, author, genre, date_read):
    """Добавление тестовой книги через UI"""
    try:
        browser.get("http://localhost:5000/add")

        # Ожидаем загрузки формы
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.book-form")))

        # Заполняем форму
        browser.find_element(By.NAME, "title").send_keys(title)
        browser.find_element(By.NAME, "author").send_keys(author)
        browser.find_element(By.NAME, "genre").send_keys(genre)

        # Используем JavaScript для установки значения в поле даты - более надежный способ
        date_field = browser.find_element(By.NAME, "date_read")
        browser.execute_script(f"arguments[0].value = '{date_read}';", date_field)

        # Нажимаем кнопку
        submit_button = browser.find_element(By.CSS_SELECTOR, "form.book-form button[type='submit']")
        submit_button.click()
        
        # Даем время странице обновиться и проверим, нет ли ошибки
        time.sleep(1)
        # Проверяем, нет ли сообщения об ошибке на той же странице (например, если валидация не прошла)
        # Это может произойти, если дата всё же не принята
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при добавлении книги после отправки формы: {error_msg}")

    except Exception as e:
        # print(f"Error adding book: {e}") # Отладка
        # print("Current URL:", browser.current_url)
        # print("Page source snippet:", browser.page_source[:500])
        raise

def test_add_book(login_user, clean_db):
    """Test adding a book via UI"""
    browser = login_user
    # clean_db фикстура уже очистила БД, дополнительно ничего не нужно

    add_test_book(browser, "Тестовая книга", "Тестовый Автор", "Фантастика", "2025-07-01")

    # Verify book appears on main page
    browser.get("http://localhost:5000/")
    # Используем явное ожидание вместо простого assert
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Тестовая книга")
        )
    except TimeoutException:
        # Если ожидание не помогло, проверим напрямую
        assert "Тестовая книга" in browser.page_source, "Книга не найдена на странице после добавления"
    assert "Тестовый Автор" in browser.page_source
    assert "Фантастика" in browser.page_source

def test_add_and_delete_book(login_user, clear_books):
    """Test adding and deleting a book"""
    browser = login_user
    # clear_books фикстура уже выполнила очистку, дополнительно вызывать не нужно

    # Add test book
    add_test_book(browser, "Книга для удаления", "Автор для удаления", "Жанр для удаления", "2025-07-01")

    # Verify book is added
    browser.get("http://localhost:5000/")
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Книга для удаления")
        )
    except TimeoutException:
        assert "Книга для удаления" in browser.page_source, "Книга для удаления не найдена на странице"

    # Delete the book
    try:
        # Явно ждем загрузки списка книг
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        
        # Находим кнопку удаления. Используем более общий XPath на случай, если стили или структура немного отличаются.
        # Предполагаем, что ссылка удаления содержит '/delete/' в href.
        delete_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/delete/') and contains(text(), '🗑️')]"))
        )
        
        # Прокручиваем к элементу на всякий случай
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_link)
        time.sleep(0.5) # Небольшая пауза после прокрутки

        # === ВАЖНО: Убираем ожидание alert ===
        # Кликаем с помощью JavaScript для надежности
        browser.execute_script("arguments[0].click();", delete_link)
        
        # === Вместо alert, просто ждем, пока книга исчезнет ===
        # Ждем некоторое время, чтобы страница обновилась или книга исчезла
        time.sleep(2) 

    except Exception as e: # Ловим любую ошибку (Timeout, NoSuchElementException, ...)
        # print("Error during delete process:")
        # print("Current URL:", browser.current_url)
        # print("Page source snippet:", browser.page_source[:500])
        raise AssertionError(f"Ошибка при попытке удалить книгу: {e}")

    # Verify book is gone from the page
    browser.get("http://localhost:5000/") # Перезагружаем страницу на всякий случай
    # Явное ожидание исчезновения текста
    try:
        WebDriverWait(browser, 10).until_not(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Книга для удаления")
        )
    except TimeoutException:
        # Если явное ожидание не помогло, проверим напрямую
        assert "Книга для удаления" not in browser.page_source, "Книга для удаления всё ещё присутствует на странице после попытки удаления"



def test_add_and_edit_book(login_user, clear_books):
    """Test adding and editing a book"""
    browser = login_user
    # clear_books фикстура уже выполнила очистку, дополнительно вызывать не нужно

    # Add test book
    add_test_book(browser, "Старое название", "Старый автор", "Старый жанр", "2025-07-01")

    # Verify book is added before trying to edit
    browser.get("http://localhost:5000/")
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Старое название")
        )
    except TimeoutException:
        assert "Старое название" in browser.page_source, "Книга для редактирования не найдена на странице"

    # Find and click edit button
    try:
        # Явно ждем загрузки списка книг
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        edit_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='book-card']//a[contains(@href, '/edit/') and contains(text(), '✏️ Редактировать')]"))
        )
        # Прокручиваем к элементу
        browser.execute_script("arguments[0].scrollIntoView(true);", edit_link)
        time.sleep(0.5) # Небольшая пауза
        
        # Кликаем с помощью JavaScript для надежности
        browser.execute_script("arguments[0].click();", edit_link)
    except (TimeoutException, NoSuchElementException) as e:
        # print("Edit button not found:")
        # print("Current URL:", browser.current_url)
        # print("Page source snippet:", browser.page_source[:500])
        raise AssertionError(f"Ошибка при попытке найти/кликнуть кнопку редактирования: {e}")

    try:
        # Wait for edit form and update fields
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "title")))
        title_input = browser.find_element(By.NAME, "title")
        author_input = browser.find_element(By.NAME, "author")
        genre_input = browser.find_element(By.NAME, "genre")
        date_read_input = browser.find_element(By.NAME, "date_read")

        # Clear and fill new data
        title_input.clear()
        title_input.send_keys("Новое название")
        author_input.clear()
        author_input.send_keys("Новый автор")
        genre_input.clear()
        genre_input.send_keys("Новый жанр")
        # Используем JS для изменения даты и здесь тоже
        browser.execute_script("arguments[0].value = '2025-08-02';", date_read_input)

        # Submit the form
        submit_button = browser.find_element(By.CSS_SELECTOR, "form.book-form button[type='submit']")
        submit_button.click()
        time.sleep(1) # Give time for redirect

        # Проверяем, нет ли ошибки после отправки формы редактирования
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при редактировании книги после отправки формы: {error_msg}")

    except Exception as e:
        # print("Error during editing:")
        # print("Current URL:", browser.current_url)
        # print("Page source snippet:", browser.page_source[:500])
        raise AssertionError(f"Ошибка во время редактирования книги: {e}")

    # Verify changes on main page
    browser.get("http://localhost:5000/")
    # Явное ожидание появления нового названия
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Новое название")
        )
    except TimeoutException:
        assert "Новое название" in browser.page_source, "Отредактированная книга (новое название) не найдена на странице"
        
    assert "Новый автор" in browser.page_source
    assert "Новый жанр" in browser.page_source
    # Убедимся, что старая книга исчезла
    assert "Старое название" not in browser.page_source
