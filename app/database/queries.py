from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank, ServiceEnum, LocationEnum

from sqlmodel import select

import asyncio

import pprint


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


async def get_rank_by_service_location(
        location: LocationEnum,
        service: ServiceEnum,
        link_url=None) -> OrganicRank:
    """
        Arg:
        url to be retrieved from the database.
        If no url is passed, defaults to https://unitedpropertyservices.au/

        Note: Under OrganicRank table, source row contains domain name:
        unitedpropertyservices.au useful to retrive all results from
        the same domain but different slugs eg. domain/home, domain/contact

        Link row contains the full url eg. https://unitedpropertyservices.au/
    """
    if link_url is None:
        link_url = "https://unitedpropertyservices.au/"  # Defaults to united url

    async with async_session() as session:
        try:
            statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
                .where(OrganicRank.link == link_url)
            )
            results = await session.exec(statement)
            for organic_rank, keyword, location in results:
                data = {
                    "location": location.location,
                    "keyword": keyword.keywords,
                    "position": organic_rank.position,
                    "tile": organic_rank.title,
                    "link": organic_rank.link,
                    "date": organic_rank.checked_date,
                }
                print(data)
        except Exception as e:
            print(e)


async def find_unranked_keywords():
    """Find keywords if any where a url
    does not rank in the top 10 results"""
    pass


async def add_or_update_service():
    async with async_session() as session:
        statement = (
            select(Location, Keyword)
            .join(Location, Keyword.location_id == Location.id)
        )

        results = await session.exec(statement)
        location = results.all()  # .all() sqlmodel method
        pprint.pprint(location)


async def check_key_words():
    async with async_session() as session:
        statement = (
            select(Keyword)
        )

        results = await session.exec(statement)
        #location = results.all()  # .all() sqlmodel method
        for keys in results:
            print(keys)


def main():
    """
    Enables running/testing functions
    as a module
    """
    #asyncio.run(check_key_words())
    #asyncio.run(add_or_update_service())
    asyncio.run(get_rank_by_service_location(LocationEnum.mr, ServiceEnum.carpet, 'https://unitedpropertyservices.au/'))
    #asyncio.run(get_keyword('carpet cleaning dunsborough'))


if __name__ == "__main__":
    main()
