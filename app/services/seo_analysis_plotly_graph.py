"""
Plotly graph objects enables more customisation 
"""

import polars as pl
from backend.app.database.queries import get_url_rank_by_service_location, \
    get_domain_rank_by_service_location
from backend.app.models import LocationEnum, ServiceEnum
import asyncio
import plotly.graph_objects as go 

# Fetch data

data_home = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.mr,
    ServiceEnum.carpet,
    'https://unitedpropertyservices.au/',)
)


# https://plotly.com/python-api-reference/generated/plotly.express.line
# NOTE: By default line charts are implemented in order they are provided
# Sorting by date stops the lines jumping backwards on the chart.
df = pl.DataFrame(data_home).sort(by='date')

# NOTE: When scattermode is set to 'group' it will override
# autorange and display 0 as min. value on yaxis 
# To fix this, assign min and max rank position from df
# and explicitly to set yaxis range under update_layout
rank_min = df['position'].min()
rank_max = df['position'].max()

fig = go.Figure()

for keyword in df['keyword'].unique():  # Manually loop over unique keyword column - plotly express does this automatically
    # Filter data for specific keyword on each iteration
    keyword_data = df.filter(pl.col('keyword') == keyword)
    
    fig.add_trace(go.Scatter(
        x=keyword_data['date'],
        y=keyword_data['position'],
        mode='lines+markers',
        name=keyword,
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
            text='Rank position'
        ),
    ),
    # Offset lines to be visible when overlap occurs
    scattermode='group',
    scattergap=0.5,  
)


fig.show()