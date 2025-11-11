import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from backend.app.database.queries import get_url_rank_by_service_location, \
    get_domain_rank_by_service_location
from backend.app.models import LocationEnum, ServiceEnum
import asyncio

# Fetch data
"""
data_home = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.duns,
    ServiceEnum.tile_grout,
    'https://unitedpropertyservices.au/',)
)
"""

data_domain = asyncio.run(get_domain_rank_by_service_location(
    LocationEnum.mr,
    ServiceEnum.carpet,
    )
)

"""
data_slug = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.duns,
    ServiceEnum.carpet,
    'https://unitedpropertyservices.au/carpet-cleaning-south-west/',)
)
"""


df = pl.DataFrame(data_domain)

print(data_domain)
print(df)