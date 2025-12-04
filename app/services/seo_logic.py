from backend.app.database.queries import get_url_rank_by_service_location, \
    get_domain_rank_by_service_location, find_unranked_keywords
import asyncio


async def fetch_ranked_and_unranked_data(location_enum, service_enum, url):
    """Fetches all data concurrently"""
    ranked, unranked = await asyncio.gather(
        get_url_rank_by_service_location(
            location_enum,
            service_enum,
            url
        ),
        find_unranked_keywords(
            location_enum,
            service_enum,
            url
        ),
    )
    return ranked, unranked


def get_earliest_ids(data) -> set:
    """
    Retrieve the keyword.id from
    keywords that were added to the
    database on the earliest recorded
    date.

    Args:
        Takes the rank results from
        fetch_ranked_and_unraked_data
        function
    """

    # Get all dates in the column
    all_dates = [d['date']for d in data]
    # Get earliest (minimum) date
    earliest_date = min(all_dates)
    ids = set([])  # Set to avoid duplicates
    for d in data:
        date = d['date']
        if date == earliest_date:
            i = d['id']
            ids.add(i)
    return ids


def get_recently_ranked_keyword(data, ids: set):
    """
    Identify newly ranked keywords.
    This function will return keywords
    that were not ranking in the top 10
    when keywords data was first saved
    in the database

    Args:
        1.Takes the rank results from
        fetch_ranked_and_unraked_data function

        2. Takes ids set from
        get_earliest_ids function
    """
    ids_set = ids
    newly_ranked = set([])  # Use set to avoid duplicates
    new = []
    for d in data:
        id = d['id']
        if id not in ids_set:
            # NOTE: this loop can retrieve
            # additional dates for when the keyword's
            # ranking was checked. However, in this function
            n = d['keyword']
            newly_ranked.add(n)
    # NOTE: Polars DataFrame Constructor cannot
    # be called with type 'set'
    # Create list of dictionary from
    # newly_rank set into to be
    # converted into a polars DataFrame
    for key in newly_ranked:
        n = {
            'keyword': key
        }
        new.append(n)

    return new
