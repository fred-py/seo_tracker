from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank


# https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/create-and-update-relationships/#create-instances-with-relationship-attributes
async def save_organic_results(data: list[dict]):
    """
     Save organic search results to database.

    Args:
        data: List of search result dictionaries from SERP API 
    Usage:

        await save_organic_results(api_response_data)
    """
    async with async_session() as session:
        area = Location(location=data[0]['location'])  # Only add the location once

        for item in data:
            search_term = Keyword(
                keywords=item['keyword'],
                date=item['date'],
                location=area,  # location is set to create relationship with Location model
            )
            # List comprehension to add ranks at once
            # As opposed to adding a rank after each iteration on traditional loop
            rank = [
                OrganicRank(
                    title=rank_item['title'],
                    source=rank_item['source'],
                    position=rank_item['position'],
                    link=rank_item['link'],
                    keyword=search_term,  # Set relationship between OrganicRank and Keyword model.
                )
                for rank_item in item['rank']
            ]
            session.add_all(rank)  # Add all ranks at once 
        await session.commit()
