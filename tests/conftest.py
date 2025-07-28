# tests/conftest.py
import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options # Импортируем Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from book_tracker import create_app
from book_tracker.extensions import db
from book_tracker.models import Book, User # Импортируем User для создания таблицы


@pytest.fixture(scope='session')
def app():
    """Создает экземпляр приложения Flask для тестирования."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        # Используем in-memory DB для тестов для изоляции
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False, # Отключаем CSRF для тестов
        'SECRET_KEY': 'test-secret-key-for-e2e'
    })
    yield app


@pytest.fixture(scope='function')
def clean_db(app):
    """Очищает базу данных и создает схему перед каждым тестом."""
    with app.app_context():
        db.drop_all()
        db.create_all() # Теперь знает о Book и User благодаря импорту выше

        # Создаем тестового пользователя, если его еще нет
        if not User.query.filter_by(username="testuser").first():
            test_user = User(username="testuser")
            # Предполагается, что метод set_password существует в модели User
            test_user.set_password("password")
            db.session.add(test_user)
            db.session.commit()

        yield db

        # Очистка после теста (обычно не требуется для in-memory DB)
        # db.session.remove() # Опционально


@pytest.fixture(scope='function')
def client(app, clean_db):
    """Создает тестовый клиент Flask."""
    return app.test_client()


# --- Фикстуры для E2E ---

@pytest.fixture(scope='function')
def browser():
    """Запускает и останавливает браузер для E2E тестов."""
    chrome_options = Options()
    # === ВКЛЮЧАЕМ HEADLESS РЕЖИМ ===
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    # Отключаем логи браузера
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # =============================

    service = Service(ChromeDriverManager().install())
    # Используем headless браузер
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Увеличиваем неявное ожидание
    driver.implicitly_wait(15)
    yield driver
    driver.quit()


@pytest.fixture(scope='function')
def clear_books(browser):
    """Очищает книги перед тестом (через UI). Это фикстура, а не вызываемая функция."""
    try:
        browser.get("http://localhost:5000/")
        # Даем время странице загрузиться
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-list"))
        )
        time.sleep(1) # Дополнительная задержка для стабильности

        # Повторяем, пока кнопки удаления находятся
        while True:
            try:
                # Находим кнопку удаления (искать внутри book-card)
                delete_btn = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='book-card']//a[contains(@href, '/delete/')]"))
                )
                # Прокручиваем к кнопке, если она вне видимости
                browser.execute_script("arguments[0].scrollIntoView(true);", delete_btn)
                time.sleep(0.5) # Небольшая пауза после прокрутки

                # Кликаем с помощью JavaScript для надежности
                browser.execute_script("arguments[0].click();", delete_btn)

                # Обрабатываем алерт подтверждения
                try:
                    WebDriverWait(browser, 5).until(EC.alert_is_present())
                    alert = browser.switch_to.alert
                    alert.accept()
                    # Ждем, пока страница перезагрузится или элемент исчезнет
                    time.sleep(1)
                except Exception as e:
                    # print(f"Warning: Could not handle alert or page reload after delete: {e}")
                    # Даже если алерт не появился, продолжаем
                    pass

            except Exception:
                # Если кнопка не найдена или не кликабельна, значит, книги закончились
                # print("No more delete buttons found or error occurred.")
                break

    except Exception as e:
        # print(f"Error during clear_books fixture: {e}")
        # Не критично, если очистка не удалась, тесты должны сами справляться
        pass

    # Эта фикстура ничего не возвращает, она просто выполняет очистку


@pytest.fixture(scope='function')
def login_user(browser, clean_db): # Зависим от clean_db для создания пользователя
    """Входит в систему как тестовый пользователь."""
    browser.get("http://localhost:5000/login")
    # Явное ожидание загрузки формы
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    browser.find_element(By.NAME, "username").send_keys("testuser")
    browser.find_element(By.NAME, "password").send_keys("password")
    # Более надежный способ найти кнопку отправки формы
    submit_button = browser.find_element(By.XPATH, "//form//button[@type='submit']")
    submit_button.click()
    # Явное ожидание редиректа
    try:
        WebDriverWait(browser, 10).until(
             EC.url_contains("/")) # Проверяем, что URL изменился
    except:
        # Если ожидание не удалось, даем немного времени
        time.sleep(2)

    return browser # Возвращаем уже залогиненный браузер