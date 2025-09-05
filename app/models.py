"""SQLModel combines SQLAlchemy with Pydentic, data validation out of the box.
Reduces redundancy, less code. 
Synchronous support to handle multiple requests concurrently"""
# https://www.youtube.com/watch?v=GONyd0CUrPc
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine


class OrganicRank(SQLModel, table=True):
    """
    table=True tells SQLModel this is a table model - Not 
    just a data model in regular Pydantic class
    """
    id: int | None = Field(default=None, primary_key=True, index=True)
    location: str = Field(index=True)
    keywords: str = Field(index=True)
    title: Optional[str] = Field(index=True)
    source: Optional[str] = Field(index=True)
    position: int = Field(index=True)
    link: Optional[str] = Field(index=True)

    #def to_json(self) -> dict:
      # """Serialise onject to JSON"""
    #    pass

    #def __repr__(self) -> str:
    #    return f'Id: {self.id}, ' \
    #            f'Location: {self.location}, ' \
    #            f'Keywords: {self.keywords}, ' \
    #            f'Title: {self.title}, ' \
     #           f'Source: {self.source}, ' \
     #          f'Position: {self.position}, ' \
     #          f'Link: {self.link}, '