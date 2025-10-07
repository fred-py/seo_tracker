from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank

from sqlmodel import select

import asyncio


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
                created_date=item['created_date'],
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


async def retrieve_target_url(source_url=None) -> OrganicRank:
    """
        Arg:
        url to be retrieved from the database.
        If no url is passed, defaults to unitedpropertyservices.au
    """
    if source_url is None:
        source_url = "unitedpropertyservices.au"  # Defaults to united url
    async with async_session() as session:
        statement = (
            select(OrganicRank, Keyword, Location)
            .join(Keyword, OrganicRank.keyword_id == Keyword.id)
            .join(Location, Keyword.location_id == Location.id)
            .where(OrganicRank.source == source_url)
        )
        results = await session.exec(statement)
        for organic_rank, keyword, location in results:
            data = {
                "location": location.location,
                "keyword": keyword.keywords,
                "position": organic_rank.position,
                "date": keyword.created_date,
            }
            print(data)


def main():
    """
    Enables running/testing functions
    as a module
    """
    asyncio.run(retrieve_target_url())


if __name__ == "__main__":
    main()
