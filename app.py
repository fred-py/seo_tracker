
from serpapi.google_search import GoogleSearch
import pprint

api_key = "99023a2c0c9bf6c830b6b64f6ec3ab05542781290f4739fdf28ef54a7826a832"

class GetGoogleResults:



    def __init__(self, q: str, location: str) -> None:
        self.q = q
        self.location = location

    def set_organic_params(self):
        params = {
            "engine": "google",
            "q": self.q,
            "location": self.location,
            "hl": "en",
            "gl": "au",
            "google_domain": "google.com",
            "num": "11",
            "start": "0",
            "safe": "active",
            "api_key": api_key
        }
        return params

    def set_google_local_places_params(self):
        params = {
            "engine": "google_local",
            "q": self.q,
            "location": self.location,
            "hl": "en",
            "gl": "au",
            "google_domain": "google.com",
            "num": "11",
            "start": "0",
            "safe": "active",
            "api_key": api_key
        }
        return params
    
    def get_organic_results(raw_data) -> dict:
        raw_data = search.get_dict()
        organic_results = results['organic_results']
        for r in organic_results:
            data = {
                'Title': r['title'],
                'Source': r['source'],
                'Position': r['position'],
                'link': r['link'],
                #'Snippet Highlighted Words': r['snippet_highlighted_words']
            }
            pprint.pprint(data)



params = {
  "engine": "google",
  "q": "Carpet Cleaning Margaret River",
  "location": "Margaret River, Western Australia, Australia",
  "hl": "en",
  "gl": "au",
  "google_domain": "google.com",
  "num": "11",
  "start": "0",
  "safe": "active",
  "api_key": 
}

search = GoogleSearch(params)
results = search.get_dict()
map_results = results['local_results']['places']
pprint.pprint(map_results)
organic_results = results['organic_results']

"""
for r in results:
    data = {
        'Title': r[0]['local_results']['places'],
        #'Rating': r['rating'],
        #'Reviews': r['reviews'],
        #'Service': r['type'],
        #Source': r['source'],
        #'Position': r['position'],
        #'link': r['link']

    }
    pprint.pprint(data)
"""

pprint.pprint(results)

for r in organic_results:
    data = {
        'Title': r['title'],
        'Source': r['source'],
        'Position': r['position'],
        'link': r['link'],
        #'Snippet Highlighted Words': r['snippet_highlighted_words']
    }
    pprint.pprint(data)