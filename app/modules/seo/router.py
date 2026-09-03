from fastapi import APIRouter, Depends
from .queries import fetch_ranked_and_unranked_data, \
  get_service_location_check_dates, get_services
from .models import SearchItems, CheckDate


router = APIRouter()


@router.post('/fetch_all/', tags=['fetch_all'])
async def get_ranking_data(search_param: SearchItems):
    """
    Retrieves 3 sets of data;
    ranked, unranked and dropped keywords.
    All the above data is contained within the
    response variable.

    Test router with the following: 
    
    {
      "location": "Margaret River, Western Australia, Australia",
      "service": "carpet",
      "url": "https://unitedpropertyservices.au/"
    }

    """
    try:
        response = await fetch_ranked_and_unranked_data(
              search_param.location,
              search_param.service,
              search_param.url
        )
        return response
    except Exception as e:
        return {'error': str(e), 'status': 500}


@router.get('/services/location/', tags=['services-location'])
async def fetch_services_locations():
    response = await get_services()
    return response

@router.post('/get_dates', tags=['get_dates'])
async def get_checked_dates(check_date_param: CheckDate):
    """
    This router is used to check when the latest ranking
    data was saved to the database.

    Returns service and location ranking check dates

    Arg: location and service as strings
    Output: list of dictionaries

    Testing on browser:
    {
      "location": "Margaret River, Western Australia, Australia",
      "service": "carpet"
    }
    """
    try:
        response = await get_service_location_check_dates(
              check_date_param.location,
              check_date_param.service,
        )
        return response
    except Exception as e:
        return {'error': str(e), 'status': 500}
