from abc import ABC, abstractmethod
from typing import Set, Dict, List
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
from scraper_utils import Offer
from datetime import datetime


class Scraper(ABC):

    def __init__(self, keywords:Set, conditions:Dict, excluded:Set):
        self.keywords = keywords
        self.conditions = conditions
        self.excluded_words = excluded

    def is_offer_excluded(self, offer: Offer) -> bool:
        """Checks if offer's title contains excluded words"""
        return any(word in offer.title for word in self.excluded_words)

    @staticmethod
    @abstractmethod
    def offer_info(offer_tag) -> Offer:
        pass

    @staticmethod
    @abstractmethod
    def check_offers_count(page_url: str) -> int:
        pass

    @abstractmethod
    def generate_urls(self) -> List[str]:
        pass

    @abstractmethod
    def list_offers(self, page_url: str, offers_count: int) -> Set[Offer]:
        pass

    @abstractmethod
    def get_offers(self) -> Set[Offer]:
        pass


class ScraperOLX(Scraper):
    URLS = {'base': 'https://www.olx.pl/oferty/q-',
            'inp_text':    '/',
            'price_from':  '&search[filter_float_price%3Afrom]=',
            'price_to':    '&search[filter_float_price%3Ato]=',
            'page':      '&page='}
    OFFERS_PER_PAGE = 30

    @staticmethod
    def offer_info(offer_tag) -> Offer:
        """Get offer info from offer tag"""

        offer_id = int(offer_tag.find('table')['data-id'])
        offer_details = offer_tag.find('a', class_=['link'])
        offer_title = offer_details.find('strong').text
        offer_link = offer_details['href']

        offer_price_text = offer_tag.find('p', class_='price').text.strip().replace(' ', '')
        offer_price = int(re.findall(r'\d+', offer_price_text)[0])

        return Offer(offer_id, offer_title, offer_price, offer_link, datetime.utcnow())

    @staticmethod
    def check_offers_count(page_url: str) -> int:
        """Tries to load the page and extract the number of offers available"""

        try:
            page = requests.get(page_url)
        except Exception as err:
            print("GET request fail:", err)
            return -1

        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            offers_tag = soup.find('div', attrs={"data-cy": "search_results_info_results_count"}).find('h2').text
            offers_count = int(re.findall(r'\d+', offers_tag.strip().replace(' ', ''))[0])
        except AttributeError as err:
            print("No offers found")
            return -1

        return offers_count

    def generate_urls(self) -> List[str]:
        """"Method for generating list of urls from the keywords and conditions"""

        conditions_url = '/?' + ''.join({self.URLS[con_name] + str(con_val) for (con_name, con_val) in self.conditions.items()})
        return [self.URLS['base'] + keyword.replace(' ', '-') + conditions_url for keyword in self.keywords]

    def list_offers(self, page_url: str, offers_count: int) -> Set[Offer]:
        """Iterates over offers page and parses them into a set"""

        offers = set()
        page_num = 0

        cur_page_url = page_url + self.URLS['page'] + str(page_num)
        page = requests.get(cur_page_url)

        while len(offers) < offers_count:
            cur_page_url = page_url + self.URLS['page'] + str(page_num)

            if cur_page_url not in page.url:
                page = requests.get(cur_page_url)

            content_soup = BeautifulSoup(page.text, 'html.parser')
            # offers_tags = content_soup.find(id='offers_table').find_all('div', class_='offer-wrapper')
            offers_tags = content_soup.find(id='offers_table').find_all('tr', class_='wrap')

            for offer_tag in offers_tags:
                offer = self.offer_info(offer_tag)
                offers.add(offer)

            page_num += 1

        return offers

    def is_offer_excluded(self, offer: Offer) -> bool:
        """Checks if offer's title contains excluded words"""
        return any(word in offer.title for word in self.excluded_words)

    def get_offers(self) -> Set[Offer]:
        """Scrapes the pages and returns set of offers"""
        offers_found = set()

        for page_url in self.generate_urls():
            offers_count = self.check_offers_count(page_url)

            for offer in self.list_offers(page_url, offers_count):
                if not offer.contains_words(self.excluded_words):
                    offers_found.add(offer)

        return offers_found


class ScraperSprzedajemy(Scraper):
    URLS = {'base': 'https://sprzedajemy.pl/wszystkie-ogloszenia?',
                 'inp_text':    'inp_text%5Bv%5D=',
                 'price_from':  '&inp_price%5Bfrom%5D=',
                 'price_to':    '&inp_price%5Bto%5D=',
                 'offset':      '&offset='}
    OFFERS_PER_PAGE = 30

    @staticmethod
    def offer_info(offer_tag) -> Offer:
        """Get offer info from offer tag"""

        offer_id = int(offer_tag['id'].replace('offer-', ''))
        offer_title = offer_tag.find('a', class_='offerLink').find('img')['title']
        offer_price_text = offer_tag.find('span', class_='price').text.strip().replace(' ', '')
        offer_price = int(re.findall(r'\d+', offer_price_text)[0])
        offer_link = 'https://sprzedajemy.pl' + offer_tag.find('a', class_='offerLink')['href']

        return Offer(offer_id, offer_title, offer_price, offer_link, datetime.utcnow())

    @staticmethod
    def check_offers_count(page_url: str) -> int:
        """Tries to load the page and extract the number of offers available"""

        try:
            page = requests.get(page_url)
        except Exception as err:
            print("GET request fail:", err)
            return -1

        content_soup = BeautifulSoup(page.text, 'html.parser')

        try:
            offers_tag = content_soup.find('p', class_='other_offers')
            offers_count = int(re.findall(r'\d+', offers_tag.find('em').text)[0])
        except AttributeError as err:
            print("No offers found: ", page_url)
            return -1

        return offers_count

    def generate_urls(self) -> List[str]:
        """"Method for generating list of urls from the keywords and conditions"""

        base_url = self.URLS['base'] + self.URLS['inp_text']
        conditions_url = ''.join({self.URLS[con_name] + str(con_val) for (con_name, con_val) in self.conditions.items()})
        return [base_url + urllib.parse.quote_plus(keyword) + conditions_url for keyword in self.keywords]

    def list_offers(self, page_url: str, offers_count: int) -> Set[Offer]:
        """Iterates over offers page and parses them into a set"""

        offers = set()

        cur_page_url = page_url + self.URLS['offset'] + '0'
        page = requests.get(cur_page_url)

        while len(offers) < offers_count:
            # offset = len(offers)//self.OFFERS_PER_PAGE * self.OFFERS_PER_PAGE
            offset = len(offers)
            cur_page_url = page_url + self.URLS['offset'] + str(offset)

            if cur_page_url not in page.url:
                page = requests.get(cur_page_url)

            content_soup = BeautifulSoup(page.text, 'html.parser')
            offers_tags = content_soup.find('ul', class_='list normal').find_all('li', id=lambda x: x and x.startswith('offer-'))

            for offer_tag in offers_tags:
                offer = self.offer_info(offer_tag)
                offers.add(offer)

        return offers


    def get_offers(self) -> Set[Offer]:
        """Scrapes the pages and returns set of offers"""
        offers_found = set()

        for page_url in self.generate_urls():
            offers_count = self.check_offers_count(page_url)

            for offer in self.list_offers(page_url, offers_count):
                if not offer.contains_words(self.excluded_words):
                    offers_found.add(offer)

        return offers_found
