from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest
import time

def test_edit_book(browser):
    """
    Тест: редактирование книги и проверка изменений на главной странице
    """
    # Открытие главной страницы с явным ожиданием загрузки
    browser.get("http://127.0.0.1:5000")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    # Добавляем отладочную информацию
    print("\nCurrent page URL:", browser.current_url)
    print("Page contains 'Добавить книгу':", "Добавить книгу" in browser.page_source)
    
    # Если книг нет, добавляем тестовую
    if "Пока нет ни одной книги." in browser.page_source:
        try:
            # Новый селектор для кнопки добавления
            add_link = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn-primary[href="/add"]')))
            add_link.click()
            
            # Заполняем форму
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, 'title'))).send_keys("Книга для редактирования")
            browser.find_element(By.NAME, "author").send_keys("Старый Автор")
            browser.find_element(By.NAME, "genre").send_keys("Фантастика")
            browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-26'")
            
            # Нажимаем кнопку добавления
            browser.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
            
            # Ждём появления книги на главной
            WebDriverWait(browser, 10).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Книга для редактирования")
            )
        except Exception as e:
            print("Error during book addition:", str(e))
            print("Current page:", browser.page_source[:1000])
            raise

    # Кликаем по ссылке "Редактировать"
    try:
        edit_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn-primary[href^="/edit"]')))
        edit_link.click()
    except Exception as e:
        print("Edit link not found:", str(e))
        print("Current page:", browser.page_source[:1000])
        raise

    # Изменяем данные формы
    title_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, 'title')))
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
    try:
        save_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-primary')))
        save_button.click()
    except Exception as e:
        print("Save button not found:", str(e))
        print("Current page:", browser.page_source[:1000])
        raise

    # Явное ожидание обновления главной страницы
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Обновлённая книга"))
    except TimeoutException:
        print("Updated book not found on page")
        print("Current page:", browser.page_source[:1000])
        raise