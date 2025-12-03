"""
Plotly graph objects enables more customisation 
"""

import polars as pl
from backend.app.database.queries import get_url_rank_by_service_location, \
    get_domain_rank_by_service_location, find_unranked_keywords
from backend.app.models import LocationEnum, ServiceEnum
import asyncio
import plotly.graph_objects as go
import pprint


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
    newly_ranked = set([])  # Set to avoid duplicates
    for d in data:
        id = d['id']
        if id not in ids_set:
            # NOTE: this loop can retrieve
            # additional dates for when the keyword's
            # ranking was checked. However, in this function
            keyword = d['keyword']
            newly_ranked.add(keyword)

    pprint.pprint(newly_ranked)
    return newly_ranked


#'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
home_url_ranked, unranked = asyncio.run(
    fetch_ranked_and_unranked_data(
        LocationEnum.mr,
        ServiceEnum.carpet,
        'https://unitedpropertyservices.au/',
        #'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
    ))


ids = get_earliest_ids(home_url_ranked)

get_recently_ranked_keyword(home_url_ranked, ids)


# https://plotly.com/python-api-reference/generated/plotly.express.line
# NOTE: By default line charts are implemented in order they are provided
# Sorting by date stops the lines jumping backwards on the chart.
df = pl.DataFrame(home_url_ranked).sort(by='date')

df_unranked = pl.DataFrame(unranked)

#df_new = pl.DataFrame(newly_ranked)

# NOTE: When scattermode is set to 'group' it will override
# autorange and display 0 as min. value on yaxis 
# To fix this, assign min and max rank position from df
# and explicitly to set yaxis range under update_layout
rank_min = df['position'].min()
rank_max = df['position'].max()
# Select first row url
url = df['link'][0]
location = df['location'][0]
service = df['service'][0]

fig = go.Figure()

for keyword in df['keyword'].unique():  # Manually loop over unique keyword column - plotly express does this automatically
    # Filter data for specific keyword on each iteration
    keyword_data = df.filter(pl.col('keyword') == keyword)
 
    fig.add_trace(go.Scatter(
        x=keyword_data['date'],
        y=keyword_data['position'],
        mode='lines+markers',
        name=keyword,
        legend='legend',
        showlegend=True,
        marker=dict(
            size=9
        )
    ))


for keywords in df_unranked['keyword']:
    keyword_data = df.filter(pl.col('keyword') == keyword)
    fig.add_trace(go.Scatter(
        x=keyword_data,
        y=keyword_data['location'],
        mode='markers',
        name=keywords,
        legend='legend2',
        showlegend=True,
        marker=dict(
            color='lightgray',
            size=8,
            symbol='x'
        ),
    ))
    

fig.update_yaxes(
    #autorange='reversed',   # set Y axis to descending order
    tickformat='d',         # Format as integers (no decimals)
    dtick=1,                # Show tick every 1 unit (optional but ensures integer spacing)

    )

fig.update_layout(
    title=dict(
        text='SEO Performance - Google Search Position Tracking',
        # xref defaults to container. Spans the entire width of the plot
        # paper refers to the width of the plotting area only
        # Setting to paper moves the title slightly to the right
        xref='paper',
        subtitle=dict(
            text=f'Location: {location}  |  Service: {service}  |  URL: {url}'
        ),
    ),

    #legend_title_text='Ranked Keywords',

    legend=dict(
        title=dict(
            text='Ranked Keywords',
        ),
        y=0.99,
        x=1.02,
        xanchor='left',
    ),
    legend2=dict(
        title=dict(
            text='Unranked Keywords',
            
        ),
        y=0.5,
        x=1.02,
        xanchor='left',
    ),

    xaxis=dict(
        title=dict(
            text='Date'
        )
    ),

    yaxis=dict(
        # To reverse yaxis range, rank_max is passed as the first argument
        # Adding/subtracting value to min and max range stops chart from
        # cutting off markers on both end eg. rank_max + 0.2
        range=[rank_max + 0.2, rank_min - 0.2],
        title=dict(
            text='Rank Position (within top 10 organic results)'
        ),
    ),

    # Offset lines to be visible when overlap occurs
    scattermode='group',
    scattergap=0.1,  
)


fig.show()