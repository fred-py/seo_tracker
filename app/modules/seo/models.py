from pydantic import BaseModel


class SearchItems(BaseModel):
    location: str
    service: str
    url: str