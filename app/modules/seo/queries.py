from app.db import async_session
from app.models import \
    Location, Keyword, OrganicRank, \
    ServiceEnum, LocationEnum
from sqlmodel import select
import asyncio
import pprint


async def get_services() -> list:
    """Retrieves services and location values"""
    try:
        async with async_session() as session:
            statement = (
                select(Location.location, Keyword.service)
                .join(Location, Keyword.location_id == Location.id)
            )
            result = await session.exec(statement)

            # Use set() to get unique values
            location = set()
            services = set()
            for loc, ser in result:
                location.add(loc)
                services.add(ser)
        return location, services

    except Exception as e:
        print(f'Error === {e}')
        raise e


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


async def find_never_ranked_keywords(
        location: str,
        service: str,
        link: str,
        ) -> list:
    """Find keywords if any, where a url
    has never ranked in the top 10 results

    Arg: LocationEnum, ServiceEnum and link/url (optional)

    Output: list of dictionaries
    """

    async with async_session() as session:
        try:
            ranked_statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
                .where(OrganicRank.link == link)
            )

            ranked = await session.exec(ranked_statement)
            # Get all keyword IDs for where domain ranks
            ranked_keyword_ids = set()  # Using set(0 to avoid duplicates and faster lookup
            # NOTE: all_time obj refers to keywords that have ranked an any
            # given point, however may no longer rank in the top 10.
            try:
                for organic, keyword, location_obj in ranked:
                    ranked_keyword_ids.add(keyword.id)

                ranked_ids = list(ranked_keyword_ids)

            except Exception as e:
                raise e

            # Get all keywords for service + location combo
            get_all_statement = (
                select(Keyword, Location)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
            )
            unranked = await session.exec(get_all_statement)
            unranked_list = list(unranked)

            # Find keywords where domain does not rank
            unranked_keys = []
            for keyword, location_obj in unranked_list:
                if keyword.id not in ranked_ids:
                    d = {
                        "location": location_obj.location,
                        "keyword": keyword.keywords,
                        "keyword_id": keyword.id,
                    }
                    unranked_keys.append(d)
            return unranked_keys

        except Exception as e:
            print(f'yeah nah something is wrong around line 240 in queries.py {e}')
            raise e


async def find_dropped_keywords(
        location: str,
        service: str,
        link: str,
        ) -> list:

    """Find keywords that have ranked then dropped
    out of the top 10 rank.

    Arg: LocationEnum, ServiceEnum and link/url (optional)

    Output: List of dicts
    """
    async with async_session() as session:
        try:
            ranked_statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
                .where(OrganicRank.link == link)
            )

            ranked = await session.exec(ranked_statement)
            # Stores all keyword IDs for where domain ranks
            ranked_keyword_ids = set()  # Using set(0 to avoid duplicates and faster lookup
            # Stores keywords IDs from most recent rank check date
            latest_ranked_keyword_ids = set()
            # IDs from dropped keywords
            dropped_ids = set()
            # NOTE: all_time obj refers to keywords that have ranked an any
            # given point, however may no longer rank in the top 10.
            all_time = []
            dates = []  # This is used to find the most recent date
            dropped = []  # List of keywords if any that have dropped out of top10
            added_keys = set()  # Keywords already added to dropped

            for organic, keyword, location_obj in ranked:
                ranked_keyword_ids.add(keyword.id)
                checked_date = organic.checked_date                
                b = {
                        "location": location_obj.location,
                        "keyword": keyword.keywords,
                        "position": organic.position,
                        "checked_date": organic.checked_date,
                        "keyword_id": keyword.id,
                    }
                all_time.append(b)

                if checked_date not in dates:
                    dates.append(checked_date)
            # Get most recent date
            latest_date = max(dates)

            for k in all_time:
                if k['checked_date'] == latest_date:
                    latest_ranked_keyword_ids.add(k['keyword_id'])
            # Get ids from keywords that have dropped out of top 10
            for i in ranked_keyword_ids:
                if i not in latest_ranked_keyword_ids:
                    dropped_ids.add(i)

            for z in all_time:
                if z['keyword_id'] in dropped_ids:
                    keyword = z['keyword']
                    # added_keys is used to avoid duplicates
                    if keyword not in added_keys:
                        y = {
                                "location": z['location'],
                                "keyword": keyword,
                                "position": z['position'],
                                "last_time_ranked": z['checked_date'],
                                "keyword_id": z['keyword_id'],
                            }
                        added_keys.add(keyword)
                        dropped.append(y)
            return dropped
        except Exception as e:
            print(
                f'something wrong in find_dropped_keywords in queries.py => ERROR: {e}'
            )


async def fetch_ranked_and_unranked_data(location: str, service: str, url: str):
    """Fetches all data concurrently"""
    ranked, unranked, dropped = await asyncio.gather(
        get_url_rank_by_service_location(
            location,
            service,
            url
        ),
        find_never_ranked_keywords(
            location,
            service,
            url
        ),
        find_dropped_keywords(
            location,
            service,
            url
        )
    )
    return {
        'ranked': ranked,
        'unranked': unranked,
        'dropped': dropped,
    }


async def get_service_location_check_dates(location: str, service: str):
    """Returns service, location and keyword ranking
        latest check dates
        
        Arg: location and service as strings
        Output: list of dictionaries

        Testing on browser:
            {
                "location": "Margaret River, Western Australia, Australia",
                "service": "carpet"
            }

    """
    async with async_session() as session:
        try:
            statement = (
                select(OrganicRank, Keyword, Location)
                .join(Keyword, OrganicRank.keyword_id == Keyword.id)
                .join(Location, Keyword.location_id == Location.id)
                .where(Keyword.service == service)
                .where(Location.location == location)
            )

            obj = await session.exec(statement)
            keyword_ids = set() # Using set to avoid duplicates
            dates = []
            data_obj = []
            data = []
            for organic_rank, keyword, location_obj in obj:
                
                checked_date = organic_rank.checked_date
                d = {
                    "location": location_obj.location,
                    "service": keyword.service,
                    "keyword": keyword.keywords,
                    "date": checked_date,
                    "keyword_id": keyword.id,
                }
                data_obj.append(d)

                if checked_date not in dates:
                    dates.append(checked_date)

            latest_date = max(dates)

            for x in data_obj:
                if x['date'] == latest_date:
                    if x['keyword_id'] not in keyword_ids:
                        y = {
                                "location": x["location"],
                                "service": x["service"],
                                "keyword": x["keyword"],
                                "date": x["date"],
                                "keyword_id": x["keyword_id"],
                            }
                        # Prevents duplicates
                        keyword_ids.add(x['keyword_id'])
                        data.append(y)
            return data
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


async def get_url_rank_by_service_location(
        location: str,
        service: str,
        link_url: str) -> OrganicRank:
    """
        Retrieves rank for single url

        Arg:
        location: must match exact string already in the database
        service: must match exact string already in the database
        url: to be retrieved from the database.

        Link row contains the full url eg. https://unitedpropertyservices.au/
    """
    
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
            data = []
            for organic_rank, keyword, location_obj in results:
                d = {
                    "location": location_obj.location,
                    "service": keyword.service,
                    "id": keyword.id,
                    "keyword": keyword.keywords,
                    "position": organic_rank.position,
                    "title": organic_rank.title,
                    "source": organic_rank.source,
                    "link": organic_rank.link,
                    "date": organic_rank.checked_date,
                }
                data.append(d)
            return data
        except Exception as e:
            print(e)


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
