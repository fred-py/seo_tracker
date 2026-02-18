from backend.app.db import async_session
from backend.app.models import Location, Keyword, OrganicRank, ServiceEnum, LocationEnum


from sqlmodel import select

import asyncio

import pprint


async def get_or_create_location(session, location_name: str) -> Location:
    """
        Helper function: Get existing location or create
        new one.

        Arg: session, location name

        Usage: called from within save_organic_results() method

        Output: returns an existing or new location object
    """
    try:
        statement = select(Location).where(Location.location == location_name)
        result = await session.exec(statement)
        location = result.first()

        if location is None:
            location = Location(location=location_name)
            session.add(location)
            await session.flush()  # Get the ID without committing.

    except Exception as e:
        # NOTE: Set up exception class once error output is clear
        print(f"Error: {e}")
        print(type(e))
        print(repr(e))

    return location


async def get_or_create_keyword(
            session,
            keyword_text: str,
            service: ServiceEnum,
            location: Location
        ) -> Keyword:
    """
        Helper function: Get existing keyword or
        create new one.

        Usage: called from within save_organic_results() method

        Output: Existing or new keyword object
    """

    try:
        statement = select(Keyword).where(
            Keyword.keywords == keyword_text,
            Keyword.location_id == location.id,
        )
        result = await session.exec(statement)
        keyword = result.first()

        if keyword is None:
            keyword = Keyword(
                keywords=keyword_text,
                location=location,
                service=service,
            )
            session.add(keyword)
            await session.flush()

    except Exception as e:
        # NOTE: Set up exception class once error output is clear
        print(f"Error: {e}")
        print(type(e))
        print(repr(e))
        raise

    return keyword


# https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/create-and-update-relationships/#create-instances-with-relationship-attributes
async def save_organic_results(
            data: list[dict],
            service: ServiceEnum,
        ):
    """
    Save organic search results to database.

    Args:
        data: List of search result dictionaries from SERP API

        service: takes ServiceEnum type
            -
    Usage:
        await save_organic_results(api_response_data)

        This function will call two helper functions:

        get_or_create_location() -> Location

            - Checks for existing location,
            if None create location.

        get_or_create_keyword() -> Keyword

            - Checks for existing keyword,
            if None create keyword:
    """
    async with async_session() as session:

        location_name = data[0]['location']
        location = await get_or_create_location(session, location_name)

        for item in data:
            keyword_text = item['keyword']
            checked_date = item['checked_date']
            keyword = await get_or_create_keyword(
                    session,
                    keyword_text,
                    service,
                    location
                )
            # List comprehension to add ranks at once
            # As opposed to adding a rank after each iteration on traditional loop
            rank = [
                OrganicRank(
                        title=rank_item['title'],
                        source=rank_item['source'],
                        position=rank_item['position'],
                        link=rank_item['link'],
                        checked_date=checked_date,
                        keyword=keyword,  # Set relationship between OrganicRank and Keyword model.
                )
                for rank_item in item['rank']
            ]
            session.add_all(rank)  # Add all ranks at once    
        await session.commit()


async def get_keywords_by_location_service(
        location: LocationEnum,
        service: ServiceEnum) -> Location:

    async with async_session() as session:
        try:
            statement = (
                select(Keyword, Location)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
            )
            results = await session.exec(statement)
            #keywords = results.all()
            data = []
            for keyword, loc in results:
                d = {
                    "location": loc.location,
                    "keyword": keyword.keywords,
                    #"service": keyword.service,
                }
                data.append(d)
            return data
            #return keywords
        except Exception as e:
            print(e)

    
def main():
    """
    Enables running/testing functions
    as a module
    """
    #asyncio.run(get_or_create_location(session, ))
    pprint.pprint(
        asyncio.run(
            get_keywords_by_location_service(
                LocationEnum.mr,
                ServiceEnum.carpet
            )
        )
    )

    #pass


if __name__ == "__main__":
    main()
