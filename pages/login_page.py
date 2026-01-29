from pages.base_page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.success_message = page.get_by_text("Products")
        self.error_message = page.get_by_text("Epic sadface:", exact=False)  # начало ошибки

    def login(self, username: str, password: str):
        self.fill(self.username, username)
        self.fill(self.password, password)
        self.click(self.login_button)