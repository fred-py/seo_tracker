from typing import Optional
from datetime import date
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum

from sqlalchemy import UniqueConstraint


# ** GLOBAL MODELS **
class ServiceEnum(str, Enum):
    carpet = "carpet"
    upholstery = "upholstery"
    leather = "leather"
    tile_grout = "tile_grout"
    vinyl = "vinyl"
    concrete = "concrete"
    curtains = "curtains"
    water_damage = "water_damage"


class LocationEnum(str, Enum):
    mr = 'Margaret River, Western Australia, Australia'
    bus = 'Busselton, Western Australia, Australia'
    duns = 'Dunsborough, Western Australia'


class Location(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    location: str = Field(index=True, unique=True)

    keywords: list['Keyword'] = Relationship(back_populates='location')


class Keyword(SQLModel, table=True):
    """Location model is unique, Keyword model can have duplicate
    keywords however keyword + location combos must be unique
    __table_args__ explicitly define the combo constraint"""

    __table_args__ = (UniqueConstraint('keywords', 'location_id'),)
    id: int | None = Field(default=None, primary_key=True, index=True)
    keywords: str = Field(index=True)
    # Service was added after data had been saved,
    # hence is set to optional
    service: str | None = Field(default=None, index=True)
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
    checked_date: date | None = Field(default=None, index=True)
    keyword_id: int = Field(foreign_key='keyword.id')
    keyword: Keyword = Relationship(back_populates='results')
