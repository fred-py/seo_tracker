from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank

from sqlmodel import select

import asyncio


async def get_keyword(keyword_text):
    async with async_session() as session:
        statement = select(Keyword).where(Keyword.keywords == keyword_text)
        result = await session.exec(statement)
    return result.first()


async def get_rankings(
        city: str | None,
        keyword_text: str | None = None) -> list[dict]:
    """
        Arg:
        Optional city and keywords argument
    """
    async with async_session() as session:
        statement = (
            select(Location, Keyword, OrganicRank)
            .join(Location, Keyword.location_id == Location.id)
            #.join(Keyword, OrganicRank.keyword_id == Keyword.id)
        )
        if city:
            statement = statement.where(Location.location == city)
        if keyword_text:
            statement = statement.where(
                Keyword.keywords.ilike(f'%{keyword_text}%'))

        results = await session.exec(statement)
        for location, keyword, organic_rank in results:
            data = {
                "location_id": location.id,
                "keyword_id": keyword.id,
                "location": location.location,
                "keyword": keyword.keywords,
                "position": organic_rank.position,
                "date": keyword.created_date,
            }
            print(data)


async def get_rankings_by_location(location: str, source_url=None) -> OrganicRank:
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
            .where(Location.location == location)
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
    asyncio.run(get_rankings_by_location('Dunsborough, Western Australia', 'unitedpropertyservices.au'))
    #asyncio.run(get_keyword('carpet cleaning dunsborough'))


if __name__ == "__main__":
    main()
