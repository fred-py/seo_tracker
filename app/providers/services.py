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
        Returns API key if enough 'total_searches_left'
            
        NOTE: FINISH THIS MAYBE USE A GET REQUES FUNC AND CALL IT FROM 
        check_searches_left
    """    
    k_1 = check_searches_left(key1)
    k_2 = check_searches_left(key2)
    
    if k_1 is True:
        return k_1
    elif k_2 is True:
        return k_2
    else:
        print('No searches left on the api key(s)')
    




if __name__ == '__main__':
    check_searches_left(api_key)
