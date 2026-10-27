import requests
import pytest
import allure
from typing import Dict
import config

pytestmark = pytest.mark.api


@allure.feature("API Управление задачами (YouGile)")
class TestApiTasks:

    @allure.story("Создание задачи")
    @allure.title("Успешное создание задачи в колонке")
    def test_create_task(
            self,
            auth_headers: Dict[str, str],
            test_context: Dict[str, str]
    ) -> None:
        expected_title = "New Autotest Task"
        payload = {
            "title": expected_title,
            "columnId": test_context["test_column_id"]
        }

        with allure.step("Отправка POST-запроса"):
            response = requests.post(
                f"{config.BASE_URL}/tasks",
                json=payload,
                headers=auth_headers
            )
            assert response.status_code == 201, f"Ошибка: {response.text}"

        with allure.step("Получение ID созданной задачи"):
            # Безопасно достаем ID, не привязываясь к полю title в ответе POST
            task_id = response.json().get("id")
            assert task_id is not None, f"В ответе нет ID. Ответ сервера: {response.json()}"

        with allure.step("Проверка через GET, что название сохранилось"):
            # Делаем GET-запрос, чтобы получить полный объект задачи
            get_response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 200
            assert get_response.json().get("title") == expected_title, \
                f"Название не совпадает. Ответ: {get_response.json()}"

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
    def test_get_tasks_by_column(
            self,
            auth_headers: Dict[str, str],
            test_context: Dict[str, str]
    ) -> None:
        column_id = test_context["test_column_id"]
        params = {"columnId": column_id}

        with allure.step(f"GET /task-list?columnId={column_id}"):
            response = requests.get(
                f"{config.BASE_URL}/task-list",
                params=params,
                headers=auth_headers,
            )

        with allure.step("Проверка статус-кода 200 и структуры ответа"):
            assert response.status_code == 200
            data = response.json()
            if isinstance(data, dict) and "content" in data:
                assert isinstance(data["content"], list)
            else:
                assert isinstance(data, list)

    @allure.story("Перемещение задачи")
    @allure.title("Перемещение задачи в другую колонку")
    def test_move_task_to_another_column(
            self,
            auth_headers: Dict[str, str],
            create_test_task: str,
            test_context: Dict[str, str]
    ) -> None:
        task_id = create_test_task
        target_col = test_context["target_column_id"]
        payload = {"columnId": target_col}

        with allure.step("Отправка PUT-запроса для смены колонки"):
            response = requests.put(
                f"{config.BASE_URL}/tasks/{task_id}",
                json=payload,
                headers=auth_headers
            )
            assert response.status_code == 200, f"Ошибка: {response.text}"

        with allure.step("Проверка через GET, что columnId изменился"):
            get_response = requests.get(
                f"{config.BASE_URL}/tasks/{task_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 200

            # безопасное извлечение через .get()
            actual_column = get_response.json().get("columnId")
            assert actual_column == target_col, \
                f"Задача не переместилась. Ожидался {target_col}, получен {actual_column}"

    @allure.story("Негативные проверки")
    @allure.title("Создание задачи без токена")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_task_unauthorized(
            self,
            test_context: Dict[str, str]
    ) -> None:
        payload = {
            "title": "Unauthorized Task",
            "columnId": test_context["test_column_id"],
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
    def test_create_task_empty_title(
            self,
            auth_headers: Dict[str, str],
            test_context: Dict[str, str]
    ) -> None:
        payload = {
            "title": "",
            "columnId": test_context["test_column_id"],
        }
        with allure.step("POST /tasks с пустым title"):
            response = requests.post(
                f"{config.BASE_URL}/tasks",
                json=payload,
                headers=auth_headers,
            )
        with allure.step("Проверка статус-кода 400"):
            assert response.status_code == 400