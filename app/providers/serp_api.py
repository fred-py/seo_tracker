from serpapi.google_search import GoogleSearch
import pprint
import os
import json
from dotenv import load_dotenv
from dateutil import tz
from datetime import datetime
from backend.app.database import save_organic_results

load_dotenv()
api_key = os.getenv('API_KEY')


d = datetime.now(tz=tz.tzlocal())
date = d.strftime('%d/%m/%Y')


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
            'api_key': api_key
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
            'date': date,
            'rank': []
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


location_1 = "Margaret River, Western Australia, Australia"
location_1_keywords = [
    "carpet cleaning margaret river",
    "carpet cleaner margaret river",
    "carpet cleaning",
    "carpet cleaning near me",
    "above & beyond carpet cleaning margaret river",
    "elite carpet cleaning",
    "rug cleaning margaret river"
]

location_2 = "Busselton, Western Australia, Australia"
location_2_keywords = [
    "carpet cleaning busselton",
    "carpet cleaning busselton wa",
    "carpet cleaner busselton",
    "carpet cleaning",
    "carpet cleaning near me",
    "carpet cleaning busselton prices",
    "elite carpet cleaning busselton",
    "prime carpet cleaning busselton",
    "professional carpet cleaner busselton",
    "rug cleaning  busselton"
]

location_3 = "Dunsborough, Western Australia"
location_3_keywords = [
        "carpet cleaner dunsborough",
        "carpet cleaning dunsborough",
        "carpet cleaners dunsborough area",
        "carpet cleaning shampoo near me",
        "carpet shampoo service near me",
        "carpet cleaning",
        "carpet cleaning near me",
        "carpet stretch and clean near me"
    ]


def main():
    location = GetGoogleResults(location_3)
    data_list = []

    for keyword in location_3_keywords:
        params = location.set_organic_params(keyword)
        raw = GoogleSearch(params)
        data = location.get_organic_results(raw, keyword)
        data_list.append(data)
    
    save_organic_results(data_list)
    pprint.pprint(data_list)

    #with open("results_test_busselton.json", "w") as f:
    #    json.dump(data_list, f, indent=2)


if __name__ == '__main__':
    main()