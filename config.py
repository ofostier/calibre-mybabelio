import json
import os


class Config:
    CALIBRE_DB_PATH = None
    QUERY_WITH_IDENTIFIER = False
    BABELIO_URL = None
    SLEEP_BETWEEN_BOOKS = 5
    NB_BOOKS_BEFORE_SLEEP = None
    SLEEP_AFTER_NB_BOOKS = None
    USE_VIRTUEL_LIBRARY_NAME = None
    USE_CALIBRE_QUERY = None
    USE_SELENIUM = None
    DEBUG = None


    def __init__(self, f):
        config = json.load(f)
        self.CALIBRE_DB_PATH = config.get("CALIBRE_DB_PATH")
        self.QUERY_WITH_IDENTIFIER = config.get("QUERY_WITH_IDENTIFIER")
        self.BABELIO_URL = config.get("BABELIO_URL")
        self.SLEEP_BETWEEN_BOOKS = config.get("SLEEP_BETWEEN_BOOKS")
        self.NB_BOOKS_BEFORE_SLEEP = config.get("NB_BOOKS_BEFORE_SLEEP")
        self.SLEEP_AFTER_NB_BOOKS = config.get("SLEEP_AFTER_NB_BOOKS")
        self.USE_VIRTUEL_LIBRARY_NAME = config.get("USE_VIRTUEL_LIBRARY_NAME")
        self.USE_CALIBRE_QUERY = config.get("USE_CALIBRE_QUERY")
        self.USE_SELENIUM = config.get("USE_SELENIUM")
        self.DEBUG = config.get("DEBUG")

config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = Config(open(config_path, "r"))
