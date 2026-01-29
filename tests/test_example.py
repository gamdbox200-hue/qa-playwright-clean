import pytest
from faker import Faker
from pages.login_page import LoginPage

fake = Faker()

@pytest.mark.parametrize("username, password, expected_success", [
    ("standard_user", "secret_sauce", True),          # правильный
    ("locked_out_user", "secret_sauce", False),       # заблокированный
    (fake.user_name(), fake.password(), False),       # рандомный фейковый
])
def test_login_various_credentials(page, username, password, expected_success):
    login_page = LoginPage(page)
    login_page.goto("https://www.saucedemo.com/")

    login_page.login(username, password)

    if expected_success:
        login_page.expect_visible(login_page.success_message)
        page.screenshot(path=f"screenshots/success_{username}.png")
    else:
        login_page.expect_visible(login_page.error_message)
        page.screenshot(path=f"screenshots/error_{username}.png")

