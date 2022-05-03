# market-scraper
Marketplace offers scraping script with Slack notifications on new offers, runs flawlessly on RPi.

ATM script can scrape 2 most popular Polish marketplace websites:
- OLX.pl
- Sprzedajemy.pl

Multiple keywords, price filtering and excluded words features are implemented. Script runs using multiple threads mechanism provided by concurrent.futures.ThreadPoolExecutor class.

In [scrapers.py](scrapers.py) template abstract class ```Scraper``` has been included, so that additional page scrapers can be added in proper fashion.

Scraper needs to be configured by providing an YAML configuration file ```config.yaml``` structured as follows:
```yaml
DB_FILENAME: scrapers_db_filename
SLACK_TOKEN: xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
SLACK_CHANNEL: '#channel_name'
KEYWORDS:
  - keyword 1
  - keyword 2
  - keyword 3
EXCLUDE:
  - exclusion 1
  - exclusion 2
  - exclusion 3
CONDITIONS:
  price_from: 1
  price_to: 10
```      