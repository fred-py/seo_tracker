from serpapi.google_search import GoogleSearch
import pprint
import os
import json
from dotenv import load_dotenv
from dateutil import tz
from datetime import datetime
from backend.app.database.crud import save_organic_results
from backend.app.models import ServiceEnum
from backend.app.providers.config import mr, bus, duns, mr_keywords, \
    mr_upholstery_keys, bus_keywords, bus_upholstery_keys, \
    duns_keywords, duns_upholstery_keys, \
    mr_tiles, bus_tiles, duns_tiles, \
    mr_curtains, duns_curtains, bus_curtains

import asyncio

load_dotenv()
api_key = os.getenv('API_KEY')
api_key_2 = os.getenv('API_KEY_2')


date_obj = datetime.now(tz=tz.tzlocal())
date = date_obj.date()


class GetGoogleResults:

    def __init__(self, location: str) -> None:
        self.location = location

    def set_organic_params(self, query):
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
            'api_key': api_key_2
        }
        return params

    def set_google_local_places_params(self, query):
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
            'api_key': api_key
        }
        return params

    def get_organic_results(self, raw_data, keyword) -> dict:
        results = raw_data.get_dict()
        #print(results)
        organic_results = results['organic_results']
        #pprint.pprint(f'Organic results for {self.q} in {self.location}')
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
                #print(data)
            return data_dict
        except TypeError as e:
            return e

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

    set_location = GetGoogleResults(location)
    data_list = []

    for keyword in keywords:
        params = set_location.set_organic_params(keyword)
        raw = GoogleSearch(params)
        data = set_location.get_organic_results(raw, keyword)
        data_list.append(data)

    #pprint.pprint(type(data_list[0]['checked_date']))
    #pprint.pprint(data_list)
    await save_organic_results(data_list, service=service)


async def save_all_concurrently():
    """Fetch and save all data concurrenlty
    in batches by service type.
    Must be done in batches to avoid rate limit."""
    
    # Carpet - Batch 1
    await asyncio.gather(
        fetch_and_save(mr, mr_keywords, ServiceEnum.carpet),
        fetch_and_save(bus, bus_keywords, ServiceEnum.carpet),
        fetch_and_save(duns, duns_keywords, ServiceEnum.carpet),
    )
    #  Add delay between batches
    await asyncio.sleep(2)

    # Upholstery
    await asyncio.gather(
        fetch_and_save(mr, mr_upholstery_keys, ServiceEnum.upholstery),
        fetch_and_save(bus, bus_upholstery_keys, ServiceEnum.upholstery),
        fetch_and_save(duns, duns_upholstery_keys, ServiceEnum.upholstery),
    )

    await asyncio.sleep(2)

    # Tiles
    await asyncio.gather(
        fetch_and_save(mr, mr_tiles, ServiceEnum.tile_grout),
        fetch_and_save(bus, bus_tiles, ServiceEnum.tile_grout),
        fetch_and_save(duns, duns_tiles, ServiceEnum.tile_grout),
    )

    await asyncio.sleep(2)

    # Curtains
    await asyncio.gather(
        fetch_and_save(mr, mr_curtains, ServiceEnum.curtains),
        fetch_and_save(bus, bus_curtains, ServiceEnum.curtains),
        fetch_and_save(duns, duns_curtains, ServiceEnum.curtains),
    )


if __name__ == '__main__':
    asyncio.run(save_all_concurrently())