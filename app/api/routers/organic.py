"""Manages organic SEO data"""


@app.get('/organic/{location}')
async def read_by_location(location: str):
    return {'location': location}