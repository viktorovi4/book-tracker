# tests\e2e\test_delete_book.py
# Импорты остаются прежними
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pytest
import time

# Импортируем add_test_book из основного файла e2e тестов
from tests.e2e.test_book_tracker_e2e import add_test_book

def test_delete_book(login_user, clear_books):
    """
    Тест: добавление книги, удаление всех книг через UI (кнопки удаления),
    проверка, что список книг пуст.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Добавляем тестовую книгу, используя уже залогиненный browser
    add_test_book(browser, "Книга для удаления 1", "Автор 1", "Жанр 1", "2025-07-01")
    # Проверим, что книга добавлена успешно, чтобы убедиться, что сессия активна
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
    except TimeoutException:
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при добавлении первой книги: {error_msg}")
        else:
             raise AssertionError("Не удалось подтвердить успешное добавление первой книги.")

    add_test_book(browser, "Книга для удаления 2", "Автор 2", "Жанр 2", "2025-07-02")
    # Проверим добавление второй книги аналогично
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
    except TimeoutException:
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при добавлении второй книги: {error_msg}")
        else:
             raise AssertionError("Не удалось подтвердить успешное добавление второй книги.")


    # 2. Переходим на главную страницу (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем, пока загрузится список книг
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        # Дополнительно проверим, что книги добавились
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Книга для удаления 1")
        )
    except TimeoutException:
        # Проверим, не оказался ли пользователь на странице логина
        # (Проверяем по содержимому, а не по URL, так как редирект может быть)
        page_text = browser.find_element(By.TAG_NAME, "body").text
        if "Войти" in page_text and ("Имя пользователя" in page_text or "Логин" in page_text or "username" in browser.page_source):
            raise AssertionError("Пользователь разлогинился. На странице отображается форма входа вместо списка книг.")
        # Если ожидание не помогло, проверим напрямую
        assert "Книга для удаления 1" in browser.page_source, "Книги не были добавлены или пользователь разлогинился"

    # 3. Удаляем все книги через UI
    try:
        # Находим все карточки книг
        book_cards = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "book-card"))
        )

        initial_count = len(book_cards)
        # print(f"Найдено {initial_count} книг для удаления.")
        for i in range(initial_count):
            # На каждой итерации заново ищем кнопку, так как DOM меняется
            delete_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='book-card']//a[contains(@href, '/delete/') and contains(text(), '🗑️')]"))
            )

            # Прокручиваем к кнопке
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
            time.sleep(0.5)

            # Кликаем с помощью JavaScript
            browser.execute_script("arguments[0].click();", delete_button)

            # Ждем, пока страница перезагрузится или книга исчезнет
            time.sleep(1.5) # Увеличиваем задержку для стабильности

    except Exception as e:
        raise AssertionError(f"Ошибка при удалении книг через UI: {e}")

    # 4. Проверяем, что список книг пуст
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1
    try:
        # Явно ждем загрузки страницы
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        # Проверяем, что тексты удаленных книг отсутствуют
        WebDriverWait(browser, 10).until_not(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Книга для удаления 1")
        )
        WebDriverWait(browser, 10).until_not(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Книга для удаления 2")
        )
    except TimeoutException:
        # Если явное ожидание не помогло, проверим напрямую
        page_source = browser.page_source
        assert "Книга для удаления 1" not in page_source
        assert "Книга для удаления 2" not in page_source

    # Дополнительная проверка: на странице должен быть текст, указывающий на пустой список
    # assert "Нет книг" in browser.page_source or "Список пуст" in browser.page_source # Адаптировать под ваш шаблон
