from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import USER_AGENT


class SeleniumDriver:
    def __init__(self):
        chrome_options = Options()

        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={USER_AGENT}")

        self.driver = webdriver.Chrome(options=chrome_options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
