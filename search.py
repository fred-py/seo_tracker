from serpapi.google_search import GoogleSearch
import pprint
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('API_KEY')


class GetGoogleResults:

    def __init__(self, location: str, q: str, ) -> None:
        self.location = location
        self.q = q

    def set_organic_params(self):
        params = {
            'engine': 'google',
            'q': self.q,
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

    def set_google_local_places_params(self):
        params = {
            'engine': 'google_local',
            'q': self.q,
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


    def get_organic_results(self, raw_data) -> dict:
        results = raw_data.get_dict()
        #print(results)
        organic_results = results['organic_results']
        #pprint.pprint(f'Organic results for {self.q} in {self.location}')
        data_list = []
        try:
            for r in organic_results:
                data = {'Keyword': self.q,
                        'Location': self.location[
                                        'Title': r['title'],
                                        'Source': r['source'],
                                        'Position': r['position'],
                                        'link': r['link']
                                    ]
                        }
                
                data_list.append(data)
                print(data_list)
            return data_list
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
                        'Title': r['title'],
                        'Position': r['position'],
                        'Reviews': r['reviews_original'],
                        'Rating': rating,
                        'Service': r['type'],
                    }
                #pprint.pprint(data)
                return data
        except KeyError as e:
            print(e)


def search_wrapper_func(query_instance) -> None:
    organic = query_instance.set_organic_params()
    results = GoogleSearch(organic)
    r = query_instance.get_organic_results(results)

    #maps = query_instance.set_google_local_places_params()
    #m_result = GoogleSearch(maps)
    #m = query_instance.get_maps_results(m_result)

    return r


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


def search_wrapper_func_2(location, query_list) -> dict:
    for keyword in query_list:
        q = GetGoogleResults(location, keyword)
        organic = q.set_organic_params()
        raw_data = GoogleSearch(organic)
        
        final = q.get_organic_results(raw_data)
        print(final)
    return final


search_wrapper_func_2(location_1, location_1_keywords)


"""
query_mr = GetGoogleResults(
    'carpet cleaning margaret river',
    'Margaret River, Western Australia, Australia')
query_b = GetGoogleResults(
    'carpet cleaning busselton',
    'Busselton, Western Australia, Australia')
query_d = GetGoogleResults(
    'carpet cleaning dunsborough',
    'Dunsborough, Western Australia, Australia')
"""

#search_wrapper_func(query_mr)
#search_wrapper_func(query_b)
#search_wrapper_func(query_d)
"""# Margaret River
organic_mr = query_mr.set_organic_params()
o_results = GoogleSearch(organic_mr)
mr = query_mr.get_organic_results(o_results)


maps_mr = query_mr.set_google_local_places_params()
m_result = GoogleSearch(maps_mr)
get_maps_results(m_result)
#---End

# Busselton
organic_b = query_b.set_organic_params()
o_results = GoogleSearch(organic_b)
get_organic_results(o_results)

maps_b = query_b.set_google_local_places_params()
m_result = GoogleSearch(maps_b)
get_maps_results(m_result)
#---End

# Dunsborough
organic_d = query_d.set_organic_params()
o_results = GoogleSearch(organic_d)
get_organic_results(o_results)

maps_d = query_d.set_google_local_places_params()
m_result = GoogleSearch(maps_d)
get_maps_results(m_result)
#---End
"""
#results = search.get_dict()
#map_results = results['local_results']['places']
#pprint.pprint(map_results)
#rganic_results = results['organic_results']