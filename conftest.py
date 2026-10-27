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

# API ФИКСТУРЫ

@pytest.fixture(scope="session")
def auth_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def test_context(auth_headers: Dict[str, str]) -> Generator[Dict[str, str], None, None]:
    """Создает уникальный проект, доску и две колонки для тестов."""
    import uuid
    unique_name = f"AutoTest_{uuid.uuid4().hex[:6]}"

    # 1. Создаем проект
    res_project = requests.post(f"{config.BASE_URL}/projects",
                                json={"title": unique_name}, headers=auth_headers)
    assert res_project.status_code == 201, f"Ошибка создания проекта: {res_project.text}"
    project_id = res_project.json()["id"]

    # 2. Создаем доску
    res_board = requests.post(f"{config.BASE_URL}/boards",
                              json={"title": "Test Board", "projectId": project_id},
                              headers=auth_headers)
    assert res_board.status_code == 201, f"Ошибка создания доски: {res_board.text}"
    board_id = res_board.json()["id"]

    # 3. Создаем ПЕРВУЮ колонку (тестовую)
    res_col1 = requests.post(f"{config.BASE_URL}/columns",
                             json={"title": "To Do", "boardId": board_id},
                             headers=auth_headers)
    assert res_col1.status_code == 201, f"Ошибка создания колонки 1: {res_col1.text}"
    column_id_1 = res_col1.json()["id"]

    # 4. Создаем ВТОРУЮ колонку (целевую)
    res_col2 = requests.post(f"{config.BASE_URL}/columns",
                             json={"title": "In Progress", "boardId": board_id},
                             headers=auth_headers)
    assert res_col2.status_code == 201, f"Ошибка создания колонки 2: {res_col2.text}"
    column_id_2 = res_col2.json()["id"]

    # 5. Возвращаем все ID
    yield {
        "project_id": project_id,
        "board_id": board_id,
        "test_column_id": column_id_1,
        "target_column_id": column_id_2
    }

    # Постусловие: удаляем проект
    requests.delete(f"{config.BASE_URL}/projects/{project_id}", headers=auth_headers)

@pytest.fixture
def create_test_task(auth_headers: Dict[str, str],
                     test_context: Dict[str, str]) -> Generator[str, None, None]:
    """Создает задачу для API-теста и удаляет её после."""
    payload = {"title": "Task for Autotest", "columnId": test_context["test_column_id"]}
    response = requests.post(f"{config.BASE_URL}/tasks", json=payload, headers=auth_headers)

    # ВАЖНО: Проверка перед извлечением ID
    assert response.status_code == 201, \
        f"Не удалось создать задачу. Код: {response.status_code}, Ответ: {response.text}"

    task_id = response.json().get("id")
    yield task_id

    requests.delete(f"{config.BASE_URL}/tasks/{task_id}", headers=auth_headers)

# UI ФИКСТУРЫ (Selenium)

@pytest.fixture(scope="function")
def browser() -> Generator[webdriver.Chrome, None, None]:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def logged_in_browser(browser: webdriver.Chrome) -> webdriver.Chrome:
    browser.get(config.UI_BASE_URL)
    wait = WebDriverWait(browser, 10)

    if "team" not in browser.current_url:
        login_btns = wait.until(EC.presence_of_all_elements_located
                                ((By.XPATH, "//*[contains(text(), 'Войти')]")))
        login_btns[0].click()

        email_input = wait.until(EC.presence_of_element_located
                                 ((By.CSS_SELECTOR, "input[type='email']")))
        email_input.send_keys(config.UI_LOGIN)

        password_input = wait.until(EC.presence_of_element_located
                                    ((By.CSS_SELECTOR, "input[type='password']")))
        password_input.send_keys(config.UI_PASSWORD)

        submit_btns = wait.until(
            EC.presence_of_all_elements_located
            ((By.XPATH, "//div[@role='button']//div[contains(text(), 'Войти')]")))
        submit_btns[-1].click()

        wait.until(EC.url_contains("/team/"))

    return browser