import httpx
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('API_KEY')
api_key_2 = os.getenv('API_KEY_2')


def check_searches_left(key) -> bool:
    """
        Takes SerpAPI key and makes a get request to
        retrieve account information.
        This function is used to check 'total_searches_left'
        before running the serp_api module.

        If 'total_searches_left' is below 179 it will return
        false.

        Note: 179 is the minimum searches required to run
        serp_api module as of 20 Apr 2026, this value
        may change if fetching for additional keywords
        and or locations.

        Param: serpapi key
        
        Output: bool
    """
    try:
        r = httpx.get(f'https://serpapi.com/account?api_key={key}')
        s = r.json()
        searches_left = s['total_searches_left']
        if searches_left > 179:
            return True
    except Exception as e:
        print(f'Error running check_searches_left() =>> {e}')
        raise e


def get_api_key(key1, key2) -> str:
    """
        This function takes 2 api keys and calls
        check_searches_left().
        
        Returns an API key if 'total_searches_left'
        is > 179.
            
        Args: 2 api keys

        Output: API Key from .env
    """
    # Using two if statements to minimise
    # get request calls to SERPAPI when
    # key1 has enough searches left
    k_1 = check_searches_left(key1)
    if k_1 is True:
        print('Calling from API Key 1')
        return k_1

    k_2 = check_searches_left(key2)
    if k_2 is True:
        print('Calling from API Key 2')
        return k_2
    else:
        print('No searches left on either keys')
        return None


# NOTE: The below is for testing only
# Functions in this module are imported
# and called from a different module
if __name__ == '__main__':
    get_api_key(api_key, api_key_2)
