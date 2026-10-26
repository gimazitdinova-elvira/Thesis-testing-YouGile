import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            # Ждем появления кнопки на странице
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

        with allure.step("Проверка перехода на страницу команды (/team/)"):
            # Убрана лишняя запятая после wait.until
            assert wait.until(
                EC.url_contains("/team/")), f"Ожидался редирект на /team/, но текущий URL: {browser.current_url}"

    @allure.story("Навигация")
    @allure.title("Проверка отображения бокового меню на дашборде")
    def test_sidebar_visible(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)
        with allure.step("Проверка видимости элементов меню"):
            # Убрана лишняя закрывающая скобка в конце
            projects_menu = wait.until(EC.visibility_of_element_located
                                       ((By.XPATH, "//*[contains(text(), 'Проекты')]")))
            assert projects_menu.is_displayed(), "Меню 'Проекты' не отображается на странице"

    @allure.story("Работа с проектами")
    @allure.title("Создание нового проекта")
    def test_create_project(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Нажатие кнопки 'Добавить проект'"):
            create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Добавить проект')]")))
            create_btn.click()

        with allure.step("Выбор типа проекта 'Проект с задачами'"):
            project_type_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Проект с задачами')]")))
            project_type_btn.click()

        with allure.step("Ввод названия проекта"):
            # Ищем поле по его атрибуту placeholder
            name_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Введите название проекта…']")))
            name_input.send_keys("UI Autotest Project")

        with allure.step("Сохранение проекта"):
            # Кликаем по кнопке "Добавить проект с задачами"
            save_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Добавить проект с задачами')]")))
            save_btn.click()

        with allure.step("Проверка, что проект появился"):
            # Ждем, пока на странице появится карточка с нашим названием
            assert wait.until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'UI Autotest Project')]"))), \
                "Созданный проект не отображается в списке"

    @allure.story("Поиск")
    @allure.title("Поиск задачи по названию")
    def test_search_task(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Ввод запроса в строку поиска"):
            # 1. Ждем, пока элемент появится в DOM
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Поиск']"))
            )

            # 2. Принудительно устанавливаем значение через JavaScript (игнорирует блокировки ввода)
            logged_in_browser.execute_script("arguments[0].value = 'QA Test Task Updated';", search_input)

            # 3. Вызываем событие 'input' или 'change', чтобы React/Vue приложение увидело изменение
            logged_in_browser.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                                             search_input)

            # 4. Отправляем Enter через JavaScript, чтобы запустить поиск
            logged_in_browser.execute_script(
                "arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter', 'bubbles': true}));",
                search_input)

        with allure.step("Проверка появления результатов"):
            results = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'QA Test Task Updated')]"))
            )
            assert len(results) > 0, "Поиск не вернул результатов"

    @allure.story("Интерфейс")
    @allure.title("Проверка переключения темы")
    def test_theme_switch(self, logged_in_browser) -> None:
        wait = WebDriverWait(logged_in_browser, 10)

        with allure.step("Открытие меню профиля"):
            profile_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Эл')]")))
            logged_in_browser.execute_script("arguments[0].click();", profile_btn)

        with allure.step("Переход в настройки"):
            settings_btn = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Настройки') or contains(text(), 'Профиль')]")))
            logged_in_browser.execute_script("arguments[0].click();", settings_btn)

        with allure.step("Прокрутка до раздела 'Внешний вид системы'"):
            # Ждем появления заголовка
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Внешний вид системы')]")))
            # Прокручиваем вниз
            logged_in_browser.execute_script("window.scrollBy(0, 300);")
            import time
            time.sleep(1)

        with allure.step("Выбор темной темы"):
            # Ищем div, внутри которого лежит SVG с цветом #2B3541
            # Используем синтаксис name() для SVG
            dark_theme_block = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[.//*[name()='rect' and @fill='#2B3541']]"))
            )

            # Кликаем по этому div через JS
            logged_in_browser.execute_script("arguments[0].click();", dark_theme_block)

        with allure.step("Проверка применения темной темы"):
            time.sleep(2)  # Ждем, пока стили применятся

            # Проверяем, что у блока с темной темой появился класс, обозначающий выбор
            # (Например, outline-accent-old, как у светлой темы в вашем HTML)
            # Или проверяем цвет фона body
            body = logged_in_browser.find_element(By.TAG_NAME, "body")
            bg_color = body.value_of_css_property("background-color")

            # Темный фон обычно имеет очень темный цвет (близкий к 0)
            # Если фон не белый - тема переключилась
            assert bg_color != "rgba(255, 255, 255, 1)", f"Тема не переключилась, фон остался белым: {bg_color}"