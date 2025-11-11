from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank, ServiceEnum, LocationEnum

from sqlmodel import select

import asyncio

import pprint

import polars as pl


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
                "keyword": keyword.keywords,
                "position": organic_rank.position,
                "keyword_id": keyword.id,
                "location": location.location,
                "date": keyword.created_date,
            }
            print(data)


async def get_url_rank_by_service_location(
        location: LocationEnum,
        service: ServiceEnum,
        link_url=None) -> OrganicRank:
    """
        Retrieves rank for single url

        Arg:
        url to be retrieved from the database.
        If no url is passed, defaults to https://unitedpropertyservices.au/

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
            print(f"HERE ARE THE DB RESULTS FOR URL RANK{results}")
            data = []
            for organic_rank, keyword, location in results:
                d = {
                    "location": location.location,
                    "keyword": keyword.keywords,
                    "position": organic_rank.position,
                    "tile": organic_rank.title,
                    "source": organic_rank.source,
                    "link": organic_rank.link,
                    "date": organic_rank.checked_date,
                }
                data.append(d)
            return data
        except Exception as e:
            print(e)


async def get_domain_rank_by_service_location(
        location: LocationEnum,
        service: ServiceEnum,
        domain=None,
        ) -> OrganicRank:
    """
        Retrieves rank for entire domain including all slugs.

        Arg:

        Location and service:
        eg. Location.Enum.mr, ServiceEnum.carpet

        domain:
        Domain name to be retrieved from the database.
        If no url is passed, defaults to unitedpropertyservices.au
        Source row contains the the domain eg. unitedpropertyservices.au
    """
    if domain is None:
        domain = "unitedpropertyservices.au"  # Defaults to united domain

    async with async_session() as session:
        try:
            statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
                .where(OrganicRank.source == domain)
            )

            ranked = await session.exec(statement)

            data = []
            for organic_rank, keyword, location_obj in ranked:
                d = {
                    "location": location_obj.location,
                    "keyword": keyword.keywords,
                    "position": organic_rank.position,
                    "source": organic_rank.source,
                    "link": organic_rank.link,
                    "title": organic_rank.title,
                    "date": organic_rank.checked_date,
                    "keyword_id": keyword.id,
                }
                data.append(d)
            return data
        except Exception as e:
            print(e)


async def find_unranked_keywords(
        location: LocationEnum,
        service: ServiceEnum,
        domain=None,
        ) -> Keyword:
    """Find keywords if any where a url
    does not rank in the top 10 results"""
    if domain is None:
        domain = "unitedpropertyservices.au"  # Defaults to united domain
    
    async with async_session() as session:
        try:
            ranked_statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
                .where(OrganicRank.source == domain)
            )

            ranked = await session.exec(ranked_statement)

            # Get all keyword IDs for where domain ranks
            ranked_keyword_ids = set()  # Using set(0 to avoid duplicates and faster lookup
            for organic_rank, keyword, location_obj in ranked:
                ranked_keyword_ids.add(keyword.id)
            
            # Get all keywords for service + location combo
            get_all_statement = (
                select(Keyword, Location)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
            )
            unranked = await session.exec(get_all_statement)
            # Find keywords where domain does not rank
            unranked_keys = []
            for keyword, location_obj in unranked:
                if keyword.id not in ranked_keyword_ids:
                    d = {
                        "location": location_obj.location,
                        "keyword": keyword.keywords,
                        "keyword_id": keyword.id,
                    }
                    unranked_keys.append(d)
            return unranked_keys            
        except Exception as e:
            print(e)


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


async def run_all_queries():
    """Run all queries in a single event loop"""
    
    # Run first query
    ranked_results = await get_domain_rank_by_service_location(
        LocationEnum.duns,
        ServiceEnum.tile_grout,
        domain='unitedpropertyservices.au'
    )
    print("Ranked Results:")
    pprint.pprint(ranked_results)
    print("###########################################")

    # Save to CSV
    if ranked_results:
        df_ranked = pl.DataFrame(ranked_results)
        df_ranked.write_csv("ranked_results.csv")
        print(f"✅ Saved {len(df_ranked)} ranked results to ranked_results.csv")
    
    # Run second query
    unranked_results = await find_unranked_keywords(
        LocationEnum.duns,
        ServiceEnum.tile_grout,
        domain='unitedpropertyservices.au'
    )
    print("Unranked Results:")
    pprint.pprint(unranked_results)
    print("###########################################")

    # Save to CSV
    if unranked_results:
        df_unranked = pl.DataFrame(unranked_results)
        df_unranked.write_csv("unranked_keywords.csv")
        print(f"✅ Saved {len(df_unranked)} unranked keywords to unranked_keywords.csv")


def main():
    """
    Enables running/testing functions
    as a module
    """

    asyncio.run(run_all_queries())

if __name__ == "__main__":
    main()
