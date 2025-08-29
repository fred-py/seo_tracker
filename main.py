from serpapi.google_search import GoogleSearch
import pprint

api_key = '99023a2c0c9bf6c830b6b64f6ec3ab05542781290f4739fdf28ef54a7826a832'


class GetGoogleResults:

    def __init__(self, q: str, location: str) -> None:
        self.q = q
        self.location = location

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
        organic_results = results['organic_results']
        pprint.pprint(f'Organic results for {self.q} in {self.location}')
        try:
            for r in organic_results:
                data = {
                    'Title': r['title'],
                    'Source': r['source'],
                    'Position': r['position'],
                    'link': r['link'],
                }
                pprint.pprint(data)
        except TypeError as e:
            return e

    def get_maps_results(self, raw_data) -> dict:

        results = raw_data.get_dict()
        m_results = results['local_results']
        pprint.pprint(f'Maps results for {self.q} in {self.location}')
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
                pprint.pprint(data)
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


query_mr = GetGoogleResults(
    'carpet cleaning margaret river',
    'Margaret River, Western Australia, Australia')
query_b = GetGoogleResults(
    'carpet cleaning busselton',
    'Busselton, Western Australia, Australia')
query_d = GetGoogleResults(
    'carpet cleaning dunsborough',
    'Dunsborough, Western Australia, Australia')


search_wrapper_func(query_mr)
search_wrapper_func(query_b)
search_wrapper_func(query_d)
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