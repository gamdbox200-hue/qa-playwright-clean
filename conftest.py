import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

@pytest.fixture(scope="session")
def browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)  # False для дебага
    yield browser
    browser.close()
    pw.stop()

@pytest.fixture(scope="function")
def context(browser: Browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    yield ctx
    ctx.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page = context.new_page()
    page.set_default_timeout(15000)  # 15 сек на действия
    page.set_default_navigation_timeout(30000)  # 30 сек на загрузку
    yield page
    page.close()

@pytest.fixture(scope="session")
def browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)  # по умолчанию без окна
    yield browser
    browser.close()
    pw.stop()

import allure

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot_path = f"screenshots/failed_{item.name}.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, name="Screenshot on failure", attachment_type=allure.attachment_type.PNG)