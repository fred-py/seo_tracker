from typing import Optional
from datetime import date
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


# ** GLOBAL MODELS **

class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    location: str = Field(index=True)

    keywords: list['Keyword'] = Relationship(back_populates='location')


class Keyword(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    keywords: str = Field(index=True)
    created_date: date = Field(index=True)
    location_id: int = Field(foreign_key='location.id')
    location: Location = Relationship(back_populates='keywords')

    results: list['OrganicRank'] = Relationship(back_populates='keyword')


class OrganicRank(SQLModel, table=True):
    """
    table=True tells SQLModel this is a table model - Not 
    just a data model in regular Pydantic class
    """
    id: int = Field(default=None, primary_key=True, index=True)
    title: Optional[str] = Field(index=True)
    source: Optional[str] = Field(index=True)
    position: int = Field(index=True)
    link: Optional[str] = Field(index=True)
        
    keyword_id: int = Field(foreign_key='keyword.id')
    keyword: Keyword = Relationship(back_populates='results')
