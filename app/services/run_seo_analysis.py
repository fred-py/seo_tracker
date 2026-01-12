"""
Plotly graph objects enables more customisation 
"""

import polars as pl
from polars.exceptions import ColumnNotFoundError

from backend.app.services.seo_logic import fetch_ranked_and_unranked_data, get_earliest_ids, \
    get_recently_ranked_keyword

from backend.app.models import LocationEnum, ServiceEnum
import asyncio
import plotly.graph_objects as go
import pprint



#'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
home_url_ranked, unranked = asyncio.run(
    fetch_ranked_and_unranked_data(
        LocationEnum.mr,
        ServiceEnum.tile_grout,
        'https://unitedpropertyservices.au/',
        #'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
    ))

pprint.pprint(home_url_ranked)
pprint.pprint(unranked)

ids = get_earliest_ids(home_url_ranked)
recent = get_recently_ranked_keyword(home_url_ranked, ids)

# https://plotly.com/python-api-reference/generated/plotly.express.line
# NOTE: By default line charts are implemented in order they are provided
# Sorting by date stops the lines jumping backwards on the chart.
df = pl.DataFrame(home_url_ranked).sort(by='date')

#df_unranked = check_unranked_keywords(unranked)

df_new = pl.DataFrame(recent)


def plot_lines_markers_ranked(fig, df, unranked):
    # Manually loop over unique keyword column - plotly express does this automatically
    for keyword in df['keyword'].unique():
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

    unranked_df = pl.DataFrame(unranked)
    try:
        for keyword in unranked_df['keyword']:
            keyword_data = unranked_df.filter(pl.col('keyword') == keyword)
            fig.add_trace(go.Scatter(
                    x=keyword_data,
                    y=keyword_data['location'],
                    mode='markers',
                    name=keyword,
                    legend='legend2',
                    showlegend=True,
                    marker=dict(
                        color='red',
                        size=8,
                        symbol='x'
                    ),
                ))
    except ColumnNotFoundError:
        return None
    
    return fig


def list_unranked_keywords(fig, unranked, ranked):
    df = pl.DataFrame(unranked)
    try:
        for keyword in df['keyword']:
            keyword_data = ranked.filter(pl.col('keyword') == keyword)
            fig.add_trace(go.Scatter(
                    x=keyword_data,
                    y=keyword_data['location'],
                    mode='markers',
                    name=keyword,
                    legend='legend2',
                    showlegend=True,
                    marker=dict(
                        color='red',
                        size=8,
                        symbol='x'
                    ),
                ))
    except ColumnNotFoundError:
        return None
    return fig


def plot_markers(data):
    pass


def check_unranked_keywords(data):
    """"""
    
    try:
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
                    color='red',
                    size=8,
                    symbol='x'
                ),
            ))
        df = pl.DataFrame(data)
        print(df)
    except ColumnNotFoundError:
        df = {
                "keyword": "All set keywords currently rank in the top 10"
            }
        return df
    return df



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

#ranked_keys = plot_lines_markers_ranked(fig, df, unranked)
#unranked_keys = list_unranked_keywords(fig, unranked, home_url_ranked)
df_unranked = pl.DataFrame(unranked)  # for loop outside function
print(df_unranked)


# NOTE: this block should come before fig.update_layout method **

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

if unranked:  # Check unranked obj instead of dataframe as empty df can be ambiguous
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
                color='red',
                size=8,
                symbol='x'
            ),
        ))

if recent:
    for keywords in df_new['keyword']:
        keyword_data = df.filter(pl.col('keyword') == keyword)
        fig.add_trace(go.Scatter(
            x=keyword_data,
            y=keyword_data['location'],
            mode='markers',
            name=keywords,
            legend='legend3',
            showlegend=True,
            marker=dict(
                color='Green',
                size=10,
                symbol='arrow'
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
    legend3=dict(
        title=dict(
            text='Recently Ranked Keywords',
            
        ),
        y=0.1,
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