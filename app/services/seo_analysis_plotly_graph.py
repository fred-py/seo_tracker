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

fig.update_yaxes(autorange='reversed')  # set Y axis to descending order

fig.show()