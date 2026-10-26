import requests
import pytest
import allure
from typing import Dict
import config

pytestmark = pytest.mark.api

@allure.feature("API Управление задачами (YouGile)")
class TestTasks:
    """Автотесты для работы с задачами YouGile."""

    @allure.story("Создание задачи")
    @allure.title("Создание задачи в колонке")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_task(self, auth_headers: Dict[str, str]) -> None:
        payload = {
            "title": "New Autotest Task",
            "columnId": config.TEST_COLUMN_ID,
        }

        with allure.step("POST /tasks — создание задачи"):
            response = requests.post(
                f"{config.BASE_URL}/tasks",
                json=payload,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 201"):
            assert response.status_code == 201, (
                f"Ожидался 201, получен {response.status_code}: {response.text}"
            )

        with allure.step("Проверка, что в ответе есть id"):
            data = response.json()
            assert "id" in data, f"В ответе нет id: {data}"
            task_id = data["id"]

        # Дополнительно: получаем задачу и проверяем поля
        with allure.step(f"GET /tasks/{task_id} — проверка полей"):
            get_response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers,
            )
            assert get_response.status_code == 200
            full_task = get_response.json()
            assert full_task["title"] == "New Autotest Task"
            assert full_task["columnId"] == config.TEST_COLUMN_ID


    @allure.story("Получение задачи")
    @allure.title("Получение задачи по ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_task_by_id(
        self,
        auth_headers: Dict[str, str],
        create_test_task: str,
    ) -> None:
        task_id = create_test_task

        with allure.step(f"GET /tasks/{task_id}"):
            response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 200 и ID"):
            assert response.status_code == 200
            assert response.json()["id"] == task_id

    @allure.story("Изменение задачи")
    @allure.title("Изменение названия задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_task_title(
            self,
            auth_headers: Dict[str, str],
            create_test_task: str,
    ) -> None:
        task_id = create_test_task
        payload = {"title": "Updated Task Title"}

        with allure.step(f"PUT /tasks/{task_id} — смена title"):
            response = requests.put(
                f"{config.BASE_URL}/tasks/{task_id}",
                json=payload,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 200"):
            assert response.status_code == 200

        # Проверяем результат отдельным GET
        with allure.step(f"GET /tasks/{task_id} — проверка нового title"):
            get_response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers,
            )
            assert get_response.status_code == 200
            assert get_response.json()["title"] == "Updated Task Title"

    @allure.story("Получение списка задач")
    @allure.title("Получение списка задач по колонке")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_tasks_by_column(self, auth_headers: Dict[str, str]) -> None:
        params = {"columnId": config.TEST_COLUMN_ID}

        with allure.step(f"GET /task-list?columnId={config.TEST_COLUMN_ID}"):
            response = requests.get(
                f"{config.BASE_URL}/task-list",
                params=params,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 200 и структуры ответа"):
            assert response.status_code == 200
            data = response.json()
            # Универсальная проверка: список или объект с пагинацией
            if isinstance(data, dict) and "content" in data:
                assert isinstance(data["content"], list)
            else:
                assert isinstance(data, list)

    @allure.story("Перемещение задачи")
    @allure.title("Перемещение задачи в другую колонку")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_move_task_to_another_column(
            self,
            auth_headers: Dict[str, str],
            create_test_task: str,
    ) -> None:
        task_id = create_test_task
        payload = {"columnId": config.TARGET_COLUMN_ID}

        with allure.step(f"PUT /tasks/{task_id} — смена columnId"):
            response = requests.put(
                f"{config.BASE_URL}/tasks/{task_id}",
                json=payload,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 200"):
            assert response.status_code == 200

        # Проверяем результат отдельным GET
        with allure.step(f"GET /tasks/{task_id} — проверка нового columnId"):
            get_response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers,
            )
            assert get_response.status_code == 200
            assert get_response.json()["columnId"] == config.TARGET_COLUMN_ID

    @allure.story("Негативные проверки")
    @allure.title("Создание задачи без токена")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_task_unauthorized(self) -> None:
        payload = {
            "title": "Unauthorized Task",
            "columnId": config.TEST_COLUMN_ID,
        }

        with allure.step("POST /tasks без заголовка Authorization"):
            response = requests.post(
                f"{config.BASE_URL}/tasks",
                json=payload,
            )

        with allure.step("Проверка статус-кода 401"):
            assert response.status_code == 401


    @allure.story("Негативные проверки")
    @allure.title("Создание задачи с пустым title")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_task_empty_title(self, auth_headers: Dict[str, str]) -> None:
        payload = {
            "title": "",
            "columnId": config.TEST_COLUMN_ID,
        }

        with allure.step("POST /tasks с пустым title"):
            response = requests.post(
                f"{config.BASE_URL}/tasks",
                json=payload,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 400"):
            assert response.status_code == 400