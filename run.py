from scraper_utils import *
from scrapers import ScraperSprzedajemy, ScraperOLX


def main():
    DB_FILENAME = 'scraper_db'
    SLACK_TOKEN = ''

    keywords = {'audi coupe', 'coupe quatro', 'audi 80 quattro', 'audi b4 quattro', '80 quatro'}
    conditions = {'price_from': 1000, 'price_to': 30000}
    exclude = {"a1", "A1", "a3", "A3", "a4", "A4", "a5", "A5", "a5", "a6", "A6", "tt", "TT", "s3", "S3", "s5", "S5"}

    scraper_sprzedajemy = ScraperSprzedajemy(keywords, conditions, exclude)
    scraper_olx = ScraperOLX(keywords, conditions, exclude)

    notifier = SlackNotifier(SLACK_TOKEN, channel="#pynotify")
    database = DatabasePickler(DB_FILENAME)

    current_offers = set()

    current_offers_sprzedajemy = scraper_sprzedajemy.get_offers()
    current_offers_olx = scraper_olx.get_offers()
    current_offers = current_offers.union(current_offers_sprzedajemy, current_offers_olx)

    [notifier.notify_offer(new_offer) for new_offer in database.new_entries(current_offers, update=False)]
    [print(new_offer) for new_offer in database.new_entries(current_offers, update=False)]

    database.save()


if __name__ == "__main__":
    main()