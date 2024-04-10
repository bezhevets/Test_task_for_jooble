import time

from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

BASE_URL = "https://realtylink.org/en/properties~for-rent"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
MAX_ADS = 60


class SeleniumDriver:
    _driver: WebDriver | None = None

    @classmethod
    def get_driver(cls) -> WebDriver:
        return cls._driver

    @classmethod
    def set_driver(cls, new_driver: WebDriver) -> None:
        cls._driver = new_driver


class PropertiesLinkScraper:
    def __init__(self):
        self.driver = SeleniumDriver.get_driver()

    def next_page(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "next").click()
            return True
        except NoSuchElementException:
            return False

    def get_links_of_page(self):
        properties_links = self.driver.find_elements(
            By.CLASS_NAME, "property-thumbnail-summary-link"
        )
        return [url.get_attribute("href") for url in properties_links]

    def get_list_links(self):
        self.driver.get(BASE_URL)
        links = []

        while len(links) < MAX_ADS:
            time.sleep(0.25)

            try:
                links.extend(self.get_links_of_page())
            except StaleElementReferenceException:
                continue

            if self.next_page() is False:
                break

        return links


def get_all_links():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    with webdriver.Chrome(options=chrome_options) as scraper:
        SeleniumDriver.set_driver(scraper)
        driver = PropertiesLinkScraper()

        list_links = driver.get_list_links()
        print(list_links)
        print(len(list_links))


if __name__ == "__main__":
    get_all_links()
