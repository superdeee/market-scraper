from scraper_utils import *
from scrapers import ScraperSprzedajemy, ScraperOLX
from typing import Dict


def main(config: Dict):

    keywords = config["KEYWORDS"]
    conditions = config["CONDITIONS"]
    exclude = config["EXCLUDE"]

    scraper_sprzedajemy = ScraperSprzedajemy(keywords, conditions, exclude)
    scraper_olx = ScraperOLX(keywords, conditions, exclude)

    notifier = SlackNotifier(config["SLACK_TOKEN"], channel="#pynotify")
    database = DatabasePickler(config["DB_FILENAME"])

    current_offers = set()

    current_offers_sprzedajemy = scraper_sprzedajemy.get_offers()
    current_offers_olx = scraper_olx.get_offers()
    current_offers = current_offers.union(current_offers_sprzedajemy, current_offers_olx)

    # [notifier.notify_offer(new_offer) for new_offer in database.new_entries(current_offers, update=False)]
    [print(new_offer) for new_offer in database.new_entries(current_offers, update=False)]

    database.save()


if __name__ == "__main__":
    config = load_yaml_config("config.yaml")
    main(config)
