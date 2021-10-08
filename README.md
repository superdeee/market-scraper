# market-scraper
Marketplace offers scraping script with Slack notifications on new offers, runs flawlessly on RPi.

ATM script can scrape 2 most popular Polish marketplace websites:
- OLX.pl
- Sprzedajemy.pl

Multiple keywords, price filtering and excluded words features are implemented.

In [scrapers.py](scrapers.py) template abstract class ```Scraper``` has been included, so that additional page scrapers can be added in proper fashion.
