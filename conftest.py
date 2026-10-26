import pytest
import requests
import config
from typing import Dict, Generator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==========================================
# API ФИКСТУРЫ
# ==========================================

@pytest.fixture(scope="session")
def auth_headers() -> Dict[str, str]:
    """Заголовки авторизации для API."""
    return {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def create_test_task(auth_headers: Dict[str, str]) -> Generator[str, None, None]:
    """Создает задачу для API-теста и удаляет её после."""
    payload = {"title": "Task for Autotest", "columnId": config.TEST_COLUMN_ID}
    response = requests.post(f"{config.BASE_URL}/tasks", json=payload, headers=auth_headers)
    task_id: str = response.json().get("id")

    yield task_id

    requests.delete(f"{config.BASE_URL}/tasks/{task_id}", headers=auth_headers)


# ==========================================
# UI ФИКСТУРЫ (Selenium)
# ==========================================

# ... (импорты остаются прежними) ...

@pytest.fixture(scope="function")
def browser() -> Generator[webdriver.Chrome, None, None]:
    """Фикстура для запуска и закрытия браузера."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Открывать браузер на весь экран
    # options.add_argument("--headless")      # Раскомментируйте, если хотите скрыть окно браузера

    # Та самая строка, которую вы просили вставить:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.implicitly_wait(10)  # Неявное ожидание элементов до 10 секунд

    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def logged_in_browser(browser: webdriver.Chrome) -> webdriver.Chrome:
    """Фикстура: открывает сайт, авторизует пользователя и возвращает браузер."""
    browser.get(config.UI_BASE_URL)
    wait = WebDriverWait(browser, 10)

    if "team" not in browser.current_url:
        # 1. Первое нажатие на кнопку "Войти"
        login_btns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'Войти')]")))
        login_btns[0].click()

        # 2. Ввод логина
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_input.send_keys(config.UI_LOGIN)

        # 3. Ввод пароля
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_input.send_keys(config.UI_PASSWORD)

        # 4. Второе нажатие на кнопку "Войти"
        submit_btns = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button']//div[contains(text(), 'Войти')]")))
        submit_btns[-1].click()

        # 5. Ожидание редиректа
        wait.until(EC.url_contains("/team/"))
        return browser