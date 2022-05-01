from datetime import datetime
from dataclasses import dataclass
import pickle
from slack import WebClient
import yaml


@dataclass
class Offer:
    id: int
    title: str
    price: int
    link: str
    date: datetime

    def contains_words(self, words_list):
        return any(word in self.title for word in words_list)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class SlackNotifier(WebClient):

    def __init__(self, slack_token, channel="#general"):
        super().__init__(token=slack_token)

        self.channel = channel

    def notify_offer(self, offer: Offer):

        notification_text = offer.title + ' | ' + str(offer.price) + 'zł' + ' | ' + offer.link
        try:
            self.chat_postMessage(channel=self.channel, text=notification_text)
        except Exception as e:
            print(e.response)


class DatabasePickler:

    def __init__(self, db_filename):
        self.filename = db_filename
        self.db = set()
        self.load()

    def load(self):
        try:
            with open(self.filename, 'rb') as db_file:
                self.db = pickle.load(db_file)
        except FileNotFoundError:
            open(self.filename, "x")

    def save(self):
        with open(self.filename, 'wb') as db_file:
            pickle.dump(self.db, db_file)

    def new_entries(self, offers, update=True):
        diff = offers.difference(self.db)
        if update:
            self.db = self.db.union(diff)
        return diff

    def offers(self):
        return self.db


def load_yaml_config(filepath: str):
    with open(filepath, encoding='utf8') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    return config_dict
