from serpapi.google_search import GoogleSearch
import pprint
import os
import time
import json
from app.logs.logging_config import get_logger
from dotenv import load_dotenv
from dateutil import tz
from datetime import datetime
from app.database.crud import save_organic_results
from app.models import ServiceEnum
from app.providers.services import get_api_key
from app.providers.config import mr, bus, duns, mr_keywords, \
    mr_upholstery_keys, bus_keywords, bus_upholstery_keys, \
    duns_keywords, duns_upholstery_keys, \
    mr_tiles, bus_tiles, duns_tiles, \
    mr_curtains, duns_curtains, bus_curtains, \
    mr_leather, bus_leather, duns_leather, \
    mr_water, bus_water, duns_water

import asyncio

logger = get_logger(__name__)

sem = asyncio.Semaphore(2)

load_dotenv()
api_key = os.getenv('API_KEY')
api_key_2 = os.getenv('API_KEY_2')


date_obj = datetime.now(tz=tz.tzlocal())
date = date_obj.date()


class GetGoogleResults:

    def __init__(self, location: str) -> None:
        self.location = location

    def set_organic_params(self, query, key):
        params = {
            'engine': 'google',
            'q': query,
            'location': self.location,
            'hl': 'en',
            'gl': 'au',
            'google_domain': 'google.com',
            'num': '10',
            'start': '0',
            'safe': 'active',
            'api_key': key
        }
        return params

    def set_google_local_places_params(self, query, key):
        params = {
            'engine': 'google_local',
            'q': query,
            'location': self.location,
            'hl': 'en',
            'gl': 'au',
            'google_domain': 'google.com',
            'num': '11',
            'start': '0',
            'safe': 'active',
            'api_key': key
        }
        return params

    def get_organic_results(self, raw_data, keyword) -> dict:
        results = raw_data.get_dict()
        logger.info(f'SERPAPI raw data lenght: {len(results)}')
        try:
            organic_results = results['organic_results']
            data_dict = {
                'location': self.location,
                'keyword': keyword,
                'checked_date': date,
                'rank': [],
            }
            try:
                for r in organic_results:
                    data = {
                        'title': r['title'],
                        'source': r['source'],
                        'position': r['position'],
                        'link': r['link']
                    }
                    data_dict['rank'].append(data)
                return data_dict
            except TypeError as e:
                return e
        except KeyError as e:
            logger.debug(f'Unable to set organic_results variable \
                            Error: {e}')
            raise e
        except Exception as e:
            logger.critical(f'Unexpected error: {e}')
            raise e

    def get_maps_results(self, raw_data) -> dict:

        results = raw_data.get_dict()
        m_results = results['local_results']
        pprint.pprint(f'=======> Maps results for {self.q} in {self.location}=========>')
        try:
            for r in m_results:
                # This if statement accounts for business
                # listings with no reviews
                if r['reviews_original'] == 'No reviews':
                    rating = 'n/a'
                else:
                    rating = r['rating']
                data = {
                        'title': r['title'],
                        'position': r['position'],
                        'reviews': r['reviews_original'],
                        'rating': rating,
                        'service': r['type'],
                    }
                #pprint.pprint(data)
                return data
        except KeyError as e:
            print(e)


async def fetch_and_save(
        location: str,
        keywords: list,
        service: ServiceEnum):

    key = get_api_key(api_key, api_key_2)

    if key is None:
        return key, 'No searches left, check SerpAPI'

    set_location = GetGoogleResults(location)
    data_list = []

    for keyword in keywords:
        params = set_location.set_organic_params(keyword, key)

        max_retries = 4
        for attempt in range(max_retries):
            try:
                raw = GoogleSearch(params)
                data = set_location.get_organic_results(raw, keyword)  
                data_list.append(data)
                break  # Exit retry loop 
            except TimeoutError:
                if attempt < max_retries - 1:
                    time.sleep(4)
                    continue
                logger.debug(f"Failed after {max_retries} attempts")
                raise

    await save_organic_results(data_list, service=service)


async def limited(coro):
    async with sem:
        return await coro


async def save_all_concurrently():
    """Fetch and save all data concurrenlty
    in batches by service type.
    Must be done in batches to avoid rate limit."""

    result = await asyncio.gather(
        # Carpet
        limited(fetch_and_save(mr, mr_keywords, ServiceEnum.carpet)),
        limited(fetch_and_save(bus, bus_keywords, ServiceEnum.carpet)),
        limited(fetch_and_save(duns, duns_keywords, ServiceEnum.carpet)),

        # Upholstery
        limited(fetch_and_save(mr, mr_upholstery_keys, ServiceEnum.upholstery)),
        limited(fetch_and_save(bus, bus_upholstery_keys, ServiceEnum.upholstery)),
        limited(fetch_and_save(duns, duns_upholstery_keys, ServiceEnum.upholstery)),

        # Tiles
        limited(fetch_and_save(mr, mr_tiles, ServiceEnum.tile_grout)),
        limited(fetch_and_save(bus, bus_tiles, ServiceEnum.tile_grout)),
        limited(fetch_and_save(duns, duns_tiles, ServiceEnum.tile_grout)),

        # Curtains
        limited(fetch_and_save(mr, mr_curtains, ServiceEnum.curtains)),
        limited(fetch_and_save(bus, bus_curtains, ServiceEnum.curtains)),
        limited(fetch_and_save(duns, duns_curtains, ServiceEnum.curtains)),

        # Leather
        limited(fetch_and_save(mr, mr_leather, ServiceEnum.leather)),
        limited(fetch_and_save(bus, bus_leather, ServiceEnum.leather)),
        limited(fetch_and_save(duns, duns_leather, ServiceEnum.leather)),

        # Water Damage & Restoration
        limited(fetch_and_save(mr, mr_water, ServiceEnum.water_damage)),
        limited(fetch_and_save(bus, bus_water, ServiceEnum.water_damage)),
        limited(fetch_and_save(duns, duns_water, ServiceEnum.water_damage)),

        return_exceptions=True,
    )

    for r in result:
        if isinstance(r, Exception):
            logger.error(f'save_all_concurrently method failed: {r}')


async def fetch_save_outdated_keywords():
    """Fetch and save all data that failed
    to be saved when running save_all_concurrently
    Note: keywords and services must be updated
    manually as needed"""

    result = await asyncio.gather(

        limited(fetch_and_save(bus, bus_leather, ServiceEnum.leather)),
        return_exceptions=True,
    )

    for r in result:
        if isinstance(r, Exception):
            logger.error(f'save_all_concurrently method failed: {r}')


if __name__ == '__main__':
    #asyncio.run(save_all_concurrently())
    asyncio.run(fetch_save_outdated_keywords())