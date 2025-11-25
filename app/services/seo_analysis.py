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
"""
data_domain = asyncio.run(get_domain_rank_by_service_location(
    LocationEnum.mr,
    ServiceEnum.carpet,
    )
)
"""


data_slug = asyncio.run(get_url_rank_by_service_location(
    LocationEnum.bus,
    ServiceEnum.upholstery,
    'https://unitedpropertyservices.au/upholstery-cleaning-south-west/',)
)


df = pl.DataFrame(data_slug)
print(df)

url_col = df.select("link")
with pl.Config(fmt_str_lengths=1000, tbl_width_chars=1000):
    print(url_col)


# --- Ensure integer positions (no decimals) ---
df = df.with_columns([
    pl.col("position").cast(pl.Float64).round().cast(pl.Int64)
])

# --- Parse dates properly ---
if df.schema.get("date") == pl.Utf8:
    df = df.with_columns(
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d", strict=False)
    )

# --- Clean keywords and sort ---
df = df.with_columns(
    pl.col("keyword").str.strip_chars()
).sort(["keyword", "date"])

# --- Create the plot ---
plt.figure(figsize=(12, 6))

# Get the earliest date across all keywords for extending single-point lines
min_date = df["date"].min()

# Small offset to separate overlapping lines
offset_amount = 0.05
keywords = df["keyword"].unique().to_list()

for idx, (keyword, group_df) in enumerate(df.group_by("keyword", maintain_order=True)):
    dates = group_df["date"].to_list()
    positions = group_df["position"].to_list()
    
    # Add small offset to positions to separate overlapping lines
    offset = (idx - len(keywords)/2) * offset_amount
    positions_offset = [p + offset for p in positions]
    
    # If only one data point, extend the line back to the earliest date
    if len(dates) == 1:
        dates = [min_date, dates[0]]
        positions_offset = [positions_offset[0], positions_offset[0]]
    
    # Plot all keywords with lines and markers
    plt.plot(dates, positions_offset, marker="o", linestyle="-", linewidth=2, 
             markersize=8, label=keyword[0])

# --- Fix y-axis to show only integers ---
ax = plt.gca()
ax.invert_yaxis()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

# --- Format x-axis dates ---
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45, ha='right')

location = df.select("location").row(0)  # Selects location on the first row...
url = df.select("link").row(0)

plt.title(f"Keyword Rankings Over Time –{location}")
plt.suptitle(f"URL: {url}")
plt.xlabel("Date")
plt.ylabel("Search Position (Rank)")
plt.legend(title="Keyword", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
