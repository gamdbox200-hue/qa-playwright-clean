from pages.login_page import LoginPage
from playwright.sync_api import Page, expect

def test_invalid_credentials(page: Page):
    login_page = LoginPage(page)
    login_page.goto("https://www.saucedemo.com/")

    login_page.login("wrong_user", "wrong_pass")

    # Проверяем, что появилась ошибка
    login_page.expect_visible(login_page.error_message)

    # Дополнительно: проверяем точный текст ошибки
    expect(login_page.error_message).to_contain_text("Epic sadface: Username and password do not match")

    # Скриншот ошибки
    page.screenshot(path="screenshots/login_error.png")