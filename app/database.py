import os

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine

from sqlalchemy.orm import sessionmaker 

#from app import crud
#from app.core.config import settings
from models import Location, Keyword, OrganicRank
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = AsyncEngine(create_engine(DATABASE_URL, echo=True))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

async def init_db():
    """
    run_sync used as metadata.creat_all
    doesn't execute asynchronously
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    Uses SQLAlchemy's built-in context manager
    'with statement' to initialise and close
    sessions automatically

    Built-in exception handling included.

    For dependency injection use at router level,
    import Depends and pass it as a param on router method

    Example:
    @app.get("seo_rank/{location}")
    def_get_rank_by_location(location, db = Depends(get_db)):
        # Add logic

    Refer to page 57 Building Generative AI services with FastAPI
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/create-and-update-relationships/#create-instances-with-relationship-attributes
def save_organic_results(data):
    with Session(engine) as session:
        area = Location(location=data[0]['location'])  # Only add the location once

        for item in data:
            search_term = Keyword(
                keywords=item['keyword'],
                date=item['date'],
                location=area,  # location is set to create relationship with Location model
            )
            # List comprehension to add ranks at once
            # As opposed to adding a rank after each iteration on traditional loop
            rank = [
                OrganicRank(
                    title=rank_item['title'],
                    source=rank_item['source'],
                    position=rank_item['position'],
                    link=rank_item['link'],
                    keyword=search_term,  # Set relationship between OrganicRank and Keyword model.
                )
                for rank_item in item['rank']
            ]
            session.add_all(rank)  # Add all ranks at once 
        session.commit()