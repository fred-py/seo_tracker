import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from backend.app.database.queries import get_url_rank_by_service_location, \
    get_domain_rank_by_service_location
from backend.app.models import LocationEnum, ServiceEnum
import asyncio
import plotly.express as px 

# Fetch data

data_home = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.mr,
    ServiceEnum.carpet,
    'https://unitedpropertyservices.au/',)
)

"""
data_domain = asyncio.run(get_domain_rank_by_service_location(
    LocationEnum.mr,
    ServiceEnum.carpet,
    )
)
"""

"""
data_slug = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.duns,
    ServiceEnum.carpet,
    'https://unitedpropertyservices.au/carpet-cleaning-south-west/',)
)
"""


df = pl.DataFrame(data_home)


print(df)

# https://plotly.com/python-api-reference/generated/plotly.express.line
# NOTE: By default line charts are implemented in order they are provided
# Sorting by date stops the lines jumping backwards on the chart.

df = df.sort(by='date')


fig = px.line(
    df,
    orientation='h',
    x='date',
    y='position',
    color='keyword',
    markers=True,
    )
fig.update_yaxes(autorange='reversed')  # set Y axis to descending order
fig.update_layout(barmode='group')


fig.show()