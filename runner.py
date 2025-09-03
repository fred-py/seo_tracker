from search import GetGoogleResults, search_wrapper
from config import CONFIG


def run_config():
    config = CONFIG
    for location, keywords in config.items():
        for keyword in keywords:
            q = GetGoogleResults(keyword, location)
            search_wrapper(q)