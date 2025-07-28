# tests\e2e\test_edit_book.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest

# Импортируем add_test_book из основного файла e2e тестов
# Предполагается, что файл test_book_tracker_e2e.py находится в той же директории
# Убедитесь, что в этом файле функция add_test_book использует execute_script для даты
from tests.e2e.test_book_tracker_e2e import add_test_book


def test_edit_book(login_user, clear_books):
    """
    Тест: добавление книги, редактирование книги через UI, проверка изменений.
    """
    browser = login_user
    # clear_books фикстура уже выполнила очистку перед тестом

    # 1. Добавляем тестовую книгу
    add_test_book(browser, "Первоначальное название", "Первоначальный автор", "Первоначальный жанр", "2025-07-01")

    # Явно дожидаемся сообщения об успехе, чтобы убедиться, что книга добавлена и сессия активна
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
    except TimeoutException:
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при добавлении книги для редактирования: {error_msg}")
        else:
             raise AssertionError("Не удалось подтвердить успешное добавление книги для редактирования.")


    # 2. Переходим на главную страницу (ИСПОЛЬЗУЕМ localhost)
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1

    # Явно ждем, пока загрузится список книг и появится добавленная книга
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Первоначальное название")
        )
    except TimeoutException:
        # Проверим, не оказался ли пользователь на странице логина
        page_text = browser.find_element(By.TAG_NAME, "body").text
        if "Войти" in page_text and ("Имя пользователя" in page_text or "Логин" in page_text or "username" in browser.page_source):
            raise AssertionError("Пользователь разлогинился до перехода на главную страницу для редактирования.")
        # Иначе просто проверим напрямую
        assert "Первоначальное название" in browser.page_source, "Книга для редактирования не найдена на главной странице"


    # 3. Находим и кликаем кнопку редактирования
    try:
        # Явно ждем загрузки списка книг
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        # Находим кнопку редактирования по более надежному XPath
        edit_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='book-card']//a[contains(@href, '/edit/') and contains(text(), '✏️')]"))
        )
        # Прокручиваем к элементу
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_link)
        time.sleep(0.5) # Небольшая пауза после прокрутки

        # Кликаем с помощью JavaScript для надежности
        browser.execute_script("arguments[0].click();", edit_link)
    except (TimeoutException, NoSuchElementException) as e:
        raise AssertionError(f"Ошибка при попытке найти/кликнуть кнопку редактирования: {e}")


    # 4. Заполняем форму редактирования новыми данными
    try:
        # Ждем загрузки формы редактирования
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "title")))
        
        # Находим поля
        title_input = browser.find_element(By.NAME, "title")
        author_input = browser.find_element(By.NAME, "author")
        genre_input = browser.find_element(By.NAME, "genre")
        date_read_input = browser.find_element(By.NAME, "date_read")

        # Очищаем и заполняем новыми данными
        title_input.clear()
        title_input.send_keys("Обновленное название")
        author_input.clear()
        author_input.send_keys("Обновленный автор")
        genre_input.clear()
        genre_input.send_keys("Обновленный жанр")
        # Используем JS для изменения даты
        browser.execute_script("arguments[0].value = '2025-08-15';", date_read_input)

        # Находим и кликаем кнопку отправки
        submit_button = browser.find_element(By.CSS_SELECTOR, "form.book-form button[type='submit']")
        submit_button.click()
        time.sleep(1) # Небольшая задержка после отправки

        # Проверяем, нет ли ошибки после отправки формы редактирования
        if "alert-error" in browser.page_source:
             error_msg_elem = browser.find_element(By.CLASS_NAME, "alert-error")
             error_msg = error_msg_elem.text
             raise AssertionError(f"Ошибка при редактировании книги после отправки формы: {error_msg}")

    except Exception as e:
        raise AssertionError(f"Ошибка во время редактирования книги: {e}")


    # 5. Проверяем изменения на главной странице
    browser.get("http://localhost:5000") # <--- ИЗМЕНЕНО С 127.0.0.1
    try:
        # Явно ждем загрузки страницы и появления нового названия
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Обновленное название")
        )
        # Проверяем остальные поля
        assert "Обновленный автор" in browser.page_source
        assert "Обновленный жанр" in browser.page_source
        # Убеждаемся, что старая книга исчезла
        assert "Первоначальное название" not in browser.page_source

    except TimeoutException:
        # Проверим, не оказался ли пользователь на странице логина
        page_text = browser.find_element(By.TAG_NAME, "body").text
        if "Войти" in page_text and ("Имя пользователя" in page_text or "Логин" in page_text or "username" in browser.page_source):
            raise AssertionError("Пользователь разлогинился после редактирования.")
        # Иначе просто проверим напрямую
        assert "Обновленное название" in browser.page_source, "Отредактированная книга (новое название) не найдена на главной странице"
        assert "Обновленный автор" in browser.page_source
        assert "Обновленный жанр" in browser.page_source
        assert "Первоначальное название" not in browser.page_source
    except AssertionError:
        # Если один из обычных assert провалился
        raise
    except Exception as e:
        raise AssertionError(f"Неизвестная ошибка при проверке результатов редактирования: {e}")
