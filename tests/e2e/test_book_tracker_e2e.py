from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import tempfile
import shutil


@pytest.fixture
def browser():
    # Создаём временную директорию для профиля Chrome
    temp_dir = tempfile.mkdtemp()
    
    # Настройки браузера (headless режим)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск без GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")  # Уникальная директория
    
    # Инициализируем драйвер Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    yield driver

    # Очистка после теста
    driver.quit()
    shutil.rmtree(temp_dir)


def test_add_book(browser):
    """
    Тест: добавление книги через форму и проверка отображения на главной
    """
    # Открытие главной страницы
    browser.get("http://127.0.0.1:5000")

    # Переход на страницу добавления книги
    try:
        add_link = browser.find_element(By.LINK_TEXT, "➕ Добавить книгу")
        add_link.click()
    except Exception as e:
        print("Ошибка при переходе на страницу добавления:", str(e))
        print("Текущий URL:", browser.current_url)
        print("HTML страницы:\n", browser.page_source)
        raise

    # Заполнение формы
    browser.find_element(By.NAME, "title").send_keys("Тестовая книга")
    browser.find_element(By.NAME, "author").send_keys("Тестовый Автор")
    browser.find_element(By.NAME, "genre").send_keys("Фантастика")
    #browser.find_element(By.NAME, "date_read").send_keys("2025-06-26")  # формат YYYY-MM-DD
    # Установка даты через JS
    browser.execute_script("document.getElementsByName('date_read')[0].value = '2025-06-28'")
    
    # Отправка формы
    browser.find_element(By.TAG_NAME, "button").click()

    # Явное ожидание появления книги на главной странице
    try:
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Тестовая книга")
        )
    except TimeoutException:
        print("Ошибка: Книга не отобразилась за 10 секунд.")
        print("Текущая страница:", browser.current_url)
        print("Исходный HTML:\n", browser.page_source)
        raise

    # Проверка, что книга действительно отображается
    assert "Тестовая книга" in browser.page_source