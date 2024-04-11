import logging
import time
from typing import List

from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from config import BASE_URL, MAX_ADS
from utils.selenium_driver import SeleniumDriver


class PropertiesLinkScraper(SeleniumDriver):

    def __init__(self) -> None:
        super().__init__()

    def next_page(self) -> bool:
        try:
            self.driver.find_element(By.CLASS_NAME, "next").click()
            return True
        except NoSuchElementException:
            logging.error("Next page not found.")
            return False

    def get_links_of_page(self) -> List[str]:
        properties_links = self.driver.find_elements(
            By.CLASS_NAME, "property-thumbnail-summary-link"
        )
        return [url.get_attribute("href") for url in properties_links]

    def get_list_links(self) -> List[str]:
        self.driver.get(BASE_URL)
        links = []

        while len(links) < MAX_ADS:
            time.sleep(0.25)
            try:
                links.extend(self.get_links_of_page())
            except StaleElementReferenceException as er:
                logging.error(f"Error: {er}. Iteration skipped.")
                continue

            if self.next_page() is False:
                break

        return links[:MAX_ADS]
