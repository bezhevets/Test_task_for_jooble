import logging
import os

from scrapers.properties_links import PropertiesLinkScraper
from scrapers.property_detail import PropertyDetail
from utils.data_utils import save_data_to_json
from utils.logging_utils import log_settings

log_settings()


def main() -> None:
    with PropertiesLinkScraper() as scraper:

        logging.info("Started scraping links of ads...")
        list_links = scraper.get_list_links()
        logging.info(f"Finish. Unique links received: {len(set(list_links))}")

    logging.info("Scrape properties...")
    properties = PropertyDetail().scrape_property(list_links)

    logging.info("Saving data...")
    save_data_to_json(properties, "data.json")
    logging.info(
        f"Data saving is complete. The path to the file: {os.path.abspath('data.json')}"
    )


if __name__ == "__main__":
    main()
