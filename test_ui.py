import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import config

pytestmark = pytest.mark.ui


@allure.feature("UI Тестирование YouGile")
class TestUI:

    @allure.story("Авторизация")
    @allure.title("Успешный вход в систему (через кнопку 'Войти')")
    def test_successful_login_and_redirect(self, browser) -> None:
        with allure.step("Открытие главной страницы"):
            browser.get(config.UI_BASE_URL)
            wait = WebDriverWait(browser, 10)

        with allure.step("Первое нажатие на кнопку 'Войти' (открытие формы)"):
            login_btns = wait.until(EC.presence_of_all_elements_located
                                    ((By.XPATH, "//*[contains(text(), 'Войти')]")))
            login_btns[0].click()

        with allure.step("Ввод логина"):
            email_input = wait.until(EC.presence_of_element_located
                                     ((By.CSS_SELECTOR, "input[type='email']")))
            email_input.send_keys(config.UI_LOGIN)

        with allure.step("Ввод пароля"):
            password_input = wait.until(EC.presence_of_element_located
                                        ((By.CSS_SELECTOR, "input[type='password']")))
            password_input.send_keys(config.UI_PASSWORD)

        with allure.step("Второе нажатие на кнопку 'Войти' (отправка формы)"):
            submit_btns = wait.until(
                EC.presence_of_all_elements_located
                ((By.XPATH, "//div[@role='button']//div[contains(text(), 'Войти')]"))
            )
            submit_btns[-1].click()

        with (allure.step("Проверка перехода на страницу команды (/team/)")):
            assert wait.until(
                EC.url_contains("/team/"))
            f"Ожидался редирект на /team/, но текущий URL: {browser.current_url}"

    @allure.story("Навигация")
    @allure.title("Проверка отображения бокового меню на дашборде")
    def test_sidebar_visible(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)
        with allure.step("Проверка видимости элементов меню"):
            projects_menu = wait.until(EC.visibility_of_element_located
                                       ((By.XPATH, "//*[contains(text(), 'Проекты')]")))
            assert projects_menu.is_displayed(), "Меню 'Проекты' не отображается на странице"

    @allure.story("Работа с проектами")
    @allure.title("Создание нового проекта")
    def test_create_project(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Нажатие кнопки 'Добавить проект'"):
            create_btn = wait.until(EC.element_to_be_clickable
                                    ((By.XPATH, "//*[contains(text(), 'Добавить проект')]")))
            create_btn.click()

        with allure.step("Выбор типа проекта 'Проект с задачами'"):
            project_type_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Проект с задачами')]")))
            project_type_btn.click()

        with allure.step("Ввод названия проекта"):
            name_input = wait.until(
                EC.presence_of_element_located
                ((By.CSS_SELECTOR, "input[placeholder='Введите название проекта…']")))
            name_input.send_keys("UI Autotest Project")

        with allure.step("Сохранение проекта"):
            save_btn = wait.until(
                EC.element_to_be_clickable
                ((By.XPATH, "//*[contains(text(), 'Добавить проект с задачами')]")))
            save_btn.click()

        with allure.step("Проверка, что проект появился"):
            assert wait.until(
                EC.visibility_of_element_located
                ((By.XPATH, "//*[contains(text(), 'UI Autotest Project')]"))), \
                "Созданный проект не отображается в списке"

    @allure.story("Поиск")
    @allure.title("Поиск задачи по названию")
    def test_search_task(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Ввод запроса в строку поиска"):
            # Находим элемент в DOM (даже если он пока не кликабелен)
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Поиск']"))
            )

            # Принудительно вводим текст через JavaScript, чтобы обойти любые блокировки
            logged_in_browser.execute_script(
                "arguments[0].value = 'QA Test Task Updated';",
                search_input
            )
            # Вызываем событие 'input', чтобы Vue/React обновил состояние
            logged_in_browser.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                search_input
            )
            # Отправляем Enter через JavaScript
            logged_in_browser.execute_script(
                "arguments[0].dispatchEvent(new KeyboardEvent('keydown',"
                " {'key': 'Enter', 'bubbles': true}));",
                search_input
            )

        with allure.step("Проверка появления результатов"):
            # Ждем, пока на странице появится текст задачи
            wait.until(
                EC.presence_of_element_located
                ((By.XPATH, "//*[contains(text(), 'QA Test Task Updated')]"))
            )

    @allure.story("Интерфейс")
    @allure.title("Проверка переключения темы")
    def test_theme_switch(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Открытие меню профиля"):
            # Ищем контейнер аватарки
            profile_btn = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'hint__cnt')]")
            ))
            # Клик через JS
            logged_in_browser.execute_script("arguments[0].click();", profile_btn)

        with allure.step("Переход в настройки"):
            settings_btn = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Мой профиль') or contains(text(), 'Настройки')]")
            ))
            # Клик через JS
            logged_in_browser.execute_script("arguments[0].click();", settings_btn)

        with (allure.step("Прокрутка до раздела 'Внешний вид системы'")):
            title = wait.until(
                EC.presence_of_element_located
                ((By.XPATH, "//*[contains(text(), 'Внешний вид системы')]"))
            )
            logged_in_browser.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", title)

        with allure.step("Выбор темной темы"):
            # Ищем блок темной темы по цвету заливки rect
            dark_theme_block = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[.//*[name()='rect' and @fill='#2B3541']]")
            ))
            # Клик через JS (избегаем проблем с перекрытием и StaleElement)
            logged_in_browser.execute_script("arguments[0].click();", dark_theme_block)

        with allure.step("Проверка применения темной темы"):
            # Ждем, пока фон страницы перестанет быть белым
            wait.until(
                lambda d: d.find_element(By.TAG_NAME, "body").value_of_css_property(
                    "background-color") != "rgba(255, 255, 255, 1)"
            )
            body = logged_in_browser.find_element(By.TAG_NAME, "body")
            bg_color = body.value_of_css_property("background-color")
            assert bg_color != "rgba(255, 255, 255, 1)", f"Тема не переключилась: {bg_color}"