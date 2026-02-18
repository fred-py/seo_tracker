
def check_latest_ranked_keywords(list) -> list:
    # NOTE: **** NOT IN USE!!!
    for date in list:
        latest = max(date.date)
        print(latest)


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
    try:
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
    except ValueError as e:
        print(f'Check seo_logic module. ERROR: {e}')

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
    # newly_rank set to be
    # converted into a polars DataFrame
    for key in newly_ranked:
        n = {
            'keyword': key,
            'location': d['location']
        }
        new.append(n)

    return new