"""
Plotly graph objects enables more customisation 
"""

import polars as pl
from polars.exceptions import ColumnNotFoundError

from backend.app.services.seo_logic import get_earliest_ids, \
    get_recently_ranked_keyword

from backend.app.database.queries import fetch_ranked_and_unranked_data

from backend.app.models import LocationEnum, ServiceEnum
import asyncio
import plotly.graph_objects as go
import pprint

from datetime import datetime


#'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
home_url_ranked, unranked, dropped = asyncio.run(
    fetch_ranked_and_unranked_data(
        LocationEnum.duns,
        ServiceEnum.carpet,
        'https://unitedpropertyservices.au/',
        #'https://unitedpropertyservices.au/carpet-cleaning-busselton-margaret-river/'
    ))


#pprint.pprint(home_url_ranked)
ids = get_earliest_ids(home_url_ranked)
recent = get_recently_ranked_keyword(home_url_ranked, ids)

# https://plotly.com/python-api-reference/generated/plotly.express.line
# NOTE: By default line charts are implemented in order they are provided
# Sorting by date stops the lines jumping backwards on the chart.
df = pl.DataFrame(home_url_ranked).sort(by='date')

unranked_df = pl.DataFrame(unranked)

df_new = pl.DataFrame(recent)


def plot_lines_markers_ranked(fig, df, unranked_df, df_new) -> go.Figure:
    """
        This function plots data from rankand keywords data
        including recenlty ranked. It displays 3 legends
        highlighting ranked, unranked and recently ranked
        keywords.

        args:
            1. fig - plotly figure object
            2. df refers to ranked data object
            3. unranked_df data object
            4. df_new refers to data output from
            get_recently_ranked_keyword method

        output:
            Returns an modified plotlly fig obj
    """
    try:
        
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
    except Exception as e:
        raise e
    """
    try:
        latest_date = df['date'].max()
        for keyword in df['keyword'].unique():
            # Filter data for specific keyword on each iteration
            keyword_data = df.filter(
                (pl.col('keyword') == keyword) &
                (pl.col('date') == latest_date)
            )

            if len(keyword_data) > 0:
                fig.add_trace(go.Scatter(
                    # NOTE: x and y axis need valid values to work
                    # Will not work if both axis have string value
                    # However this is intended to display legend values only
                    # Nothing to be displayed on axis
                    # Hence using min. date from df and random int on y
                    x=[df['date'].min()],
                    y=[11],
                    mode='markers',
                    name=keyword,
                    legend='legend1',
                    showlegend=True,
                    marker=dict(
                        size=9
                    )
                ))

    except Exception as e:
        raise e
"""

    try:
        for keyword in unranked_df['keyword']:
            keyword_data = unranked_df.filter(pl.col('keyword') == keyword)
            fig.add_trace(go.Scatter(
                    # NOTE: x and y axis need valid values to work
                    # Will not work if both axis have string value
                    # However this is intended to display legend values only
                    # Nothing to be displayed on axis
                    # Hence using min. date from df and random int on y
                    x=[df['date'].min()],
                    y=[11],
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
        print('No unranked keyword outside of top 10')

    try:
        for keywords in df_new['keyword']:
            keyword_data = df_new.filter(pl.col('keyword') == keyword)
            fig.add_trace(go.Scatter(
                # NOTE: x and y axis need valid values to work
                # Will not work if both axis have string value
                # However this is intended to display legend values only
                # Nothing to be displayed on axis
                # Hence using min. date from df and random int on y
                x=[df['date'].min()],
                y=[11],
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
    except Exception as e:
        raise e
    return fig


def update_fig_layout(fig: go.Figure) -> go.Figure:
    """
    This function carries out layout updates of
    plotly figure object
    
    Args: go.Figure
    
    Output: updated go.Figure object
    """

    try:
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
                    text='All Time Ranked Keywords',
                ),
                y=0.99,
                x=1.02,
                xanchor='left',
            ),

            legend1=dict(
                title=dict(
                    text='All Time Ranked Keywords',
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
                y=0.07,
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
    except Exception as e:
        raise e

    return fig


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

fig_data = plot_lines_markers_ranked(fig, df, unranked_df, df_new)

fig_layout = update_fig_layout(fig_data)

fig_layout.show()