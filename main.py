import asyncio
import json
import logging
import os
import sys
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "https://realtylink.org/en/properties~for-rent"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
MAX_ADS = 5


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("log.log"), mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)


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


class PropertiesLinkScraper(SeleniumDriver):

    def __init__(self):
        super().__init__()

    def next_page(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "next").click()
            return True
        except NoSuchElementException:
            logging.error("Next page not found.")
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
            except StaleElementReferenceException as er:
                logging.error(f"Error: {er}. Iteration skipped.")
                continue

            if self.next_page() is False:
                break

        return links[:MAX_ADS]


class PropertyDetail:
    def change_correct_size(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params["w"] = ["1024"]
        query_params["h"] = ["1024"]
        query_params["sm"] = ["m"]
        updated_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=updated_query))
        return new_url

    def get_property_images(self, soup):
        soup2 = soup.find("div", {"class": "thumbnail last-child first-child"})
        script_tag = soup2.find("script").text
        data = json.loads(script_tag[script_tag.find("[") : script_tag.find("]") + 1])
        links = [self.change_correct_size(link) for link in data]
        return links

    def get_property_description(self, soup):
        description_tag = soup.find("div", {"itemprop": "description"})
        return description_tag.text.strip() if description_tag else None

    def get_property_square(self, soup):
        area_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 carac-container"})
        area = area_soup.find("span").text.strip().split()[0]
        return area.replace(",", "")

    def get_property_rooms(self, soup):
        bedroom_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 cac"})
        bathroom_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 sdb"})

        amount_rooms = []
        if bathroom_soup:
            bathrooms = bathroom_soup.text.split()[0]
            amount_rooms.append(int(bathrooms))

        if bedroom_soup:
            bedrooms = bedroom_soup.text.split()[0]
            amount_rooms.append(int(bedrooms))

        return sum(amount_rooms)

    def get_data(self, soup):
        address = soup.select_one('h2[itemprop="address"]').text.strip()
        return {
            "title": soup.select_one('span[data-id="PageTitle"]').text,
            "region": address.split(",")[-2:],
            "address": address,
            "description": self.get_property_description(soup),
            "images": self.get_property_images(soup),
            "price": int(soup.find("meta", {"itemprop": "price"})["content"]),
            "rooms": self.get_property_rooms(soup),
            "square": int(self.get_property_square(soup)),
        }

    async def get_property(self, link, client):
        response = await client.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        property_data = self.get_data(soup)
        return property_data

    async def create_async_task(self, links: list):
        async with httpx.AsyncClient(headers={"user-agent": USER_AGENT}) as client:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self.get_property(link, client)) for link in links
                ]

        for task in tasks:
            print(task.result())
        return tasks

    def scrape_property(self, links: list):
        return asyncio.run(self.create_async_task(links=links))


def get_all_links():
    with PropertiesLinkScraper() as scraper:

        logging.info("Started scraping links of ads...")
        list_links = scraper.get_list_links()
        logging.info(f"Finish. Unique links received: {len(set(list_links))}")

    logging.info("Scrape properties...")
    properties = PropertyDetail().scrape_property(list_links)
    logging.info(properties)


if __name__ == "__main__":
    get_all_links()
