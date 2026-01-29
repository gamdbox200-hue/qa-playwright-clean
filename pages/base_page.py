from playwright.sync_api import Page, Locator, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str):
     self.page.goto(url, timeout=60000)

    def fill(self, locator: Locator, value: str):
        locator.fill(value)

    def click(self, locator: Locator):
        locator.click()

    def expect_visible(self, locator: Locator, timeout=10000):
        expect(locator).to_be_visible(timeout=timeout)