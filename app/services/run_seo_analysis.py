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


def newly_ranked_keyword(data):
    """
    Identify newly ranked keywords.
    This function will return keywords
    that were not ranking in the top 10
    when keywords data was first saved
    in the database

    Args:
        Takes the rank results from
        fetch_ranked_and_unraked_data
        function
    """
    # Get all dates in the column
    all_dates = [d['date']for d in data]
    # Get earliest (minimum) date
    first_saved = min(all_dates)
    newly_added = []

    for d in data:
        d = data['date']
        if d not in first_saved:
            new = {
                "location": data['location'],
                "keyword": data['keyword'],
                "position": data['position'],
                "tile": data['title'],
                "source": data['source'],
                "link": data['link'],
                "date": data['checked_date'],
            }
            newly_added.append(new)

    pprint.pprint(newly_added)
    return first_saved


home_url_ranked, unranked = asyncio.run(
    fetch_ranked_and_unranked_data(
        LocationEnum.bus,
        ServiceEnum.carpet,
        'https://unitedpropertyservices.au/'
    ))

newly_ranked_keyword(home_url_ranked)

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
            text=f'Location: {location}  |  URL: {url}'
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