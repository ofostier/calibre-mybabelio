import json
import os


class Config:
    CALIBRE_DB_PATH = None
    QUERY_WITH_IDENTIFIER = False
    BABELIO_URL = None
    SLEEP_BETWEEN_BOOKS = 5
    USE_VIRTUEL_LIBRARY_NAME = None,
    USE_CALIBRE_QUERY = None,
    DEBUG = None


    def __init__(self, f):
        config = json.load(f)
        self.CALIBRE_DB_PATH = config.get("CALIBRE_DB_PATH")
        self.QUERY_WITH_IDENTIFIER = config.get("QUERY_WITH_IDENTIFIER")
        self.BABELIO_URL = config.get("BABELIO_URL")
        self.SLEEP_BETWEEN_BOOKS = config.get("SLEEP_BETWEEN_BOOKS")
        self.USE_VIRTUEL_LIBRARY_NAME = config.get("USE_VIRTUEL_LIBRARY_NAME")
        self.USE_CALIBRE_QUERY = config.get("USE_CALIBRE_QUERY")
        self.DEBUG = config.get("DEBUG")

config_path = os.path.join(os.path.dirname(__file__), "config.json")
print(config_path)
config = Config(open(config_path, "r"))
