from fastapi import APIRouter, Depends
from backend.app.modules.seo.queries import fetch_ranked_and_unranked_data
from backend.app.modules.seo.models import SearchItems
import asyncio

router = APIRouter()


@router.post('/fetch_all/', tags=['fetch_all'])
async def run_ranking_analysis(search_param: SearchItems):
    """
    Retrieves 3 sets of data;
    ranked, unranked and dropped keywords.
    All the above data is contained within the
    response variable.
    """
    response = await fetch_ranked_and_unranked_data(
            search_param.location,
            search_param.service,
            search_param.url
    )
    return response

"""
{
  "location": "Margaret River, Western Australia, Australia",
  "service": "carpet",
  "url": "https://unitedpropertyservices.au/"
}
"""