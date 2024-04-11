import asyncio
import json
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import httpx
from bs4 import BeautifulSoup

from config import USER_AGENT
from models import Property


class PropertyData:
    def change_correct_size(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params["w"] = ["1024"]
        query_params["h"] = ["1024"]
        query_params["sm"] = ["m"]
        updated_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=updated_query))
        return new_url

    def get_property_title(self, soup):
        return soup.select_one('span[data-id="PageTitle"]').text

    def get_property_address(self, soup):
        return soup.select_one('h2[itemprop="address"]').text.strip()

    def get_property_region(self, address):
        return ", ".join(address.split(", ")[-2:])

    def get_property_description(self, soup):
        description_tag = soup.find("div", {"itemprop": "description"})
        return description_tag.text.strip() if description_tag else None

    def get_property_images(self, soup):
        soup2 = soup.find("div", {"class": "thumbnail last-child first-child"})
        script_tag = soup2.find("script").text
        data = json.loads(script_tag[script_tag.find("[") : script_tag.find("]") + 1])
        links = [self.change_correct_size(link) for link in data]
        return links

    def get_property_price(self, soup):
        return int(soup.find("meta", {"itemprop": "price"})["content"])

    def get_property_rooms(self, soup):
        bedroom_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 cac"})
        bathroom_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 sdb"})

        result = {"bedrooms": 0, "bathrooms": 0}
        if bathroom_soup:
            bathrooms = bathroom_soup.text.split()[0]
            result["bathrooms"] = int(bathrooms)

        if bedroom_soup:
            bedrooms = bedroom_soup.text.split()[0]
            result["bedrooms"] = int(bedrooms)

        return result

    def get_property_square(self, soup):
        area_soup = soup.find("div", {"class": "col-lg-3 col-sm-6 carac-container"})
        area = area_soup.find("span").text.strip().split()[0]
        return int(area.replace(",", ""))


class PropertyDetail(PropertyData):

    def get_data(self, soup):
        address = self.get_property_address(soup)
        return {
            "title": self.get_property_title(soup),
            "region": self.get_property_region(address),
            "address": address,
            "description": self.get_property_description(soup),
            "images": self.get_property_images(soup),
            "price": self.get_property_price(soup),
            "rooms": self.get_property_rooms(soup),
            "square": self.get_property_square(soup),
        }

    async def get_property(self, link, client):
        try:
            response = await client.get(link, timeout=5)
            soup = BeautifulSoup(response.content, "html.parser")
            property_data = self.get_data(soup)
            return Property(link=link, **property_data)
        except httpx.ConnectTimeout as error:
            logging.error(f"Error: {error}")

    async def create_async_task(self, links: list):
        async with httpx.AsyncClient(headers={"user-agent": USER_AGENT}) as client:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self.get_property(link, client)) for link in links
                ]
        return [task.result() for task in tasks]

    def scrape_property(self, links: list):
        return asyncio.run(self.create_async_task(links=links))
