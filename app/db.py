import os
from pathlib import Path

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv


# parent property moves up one directory level each time it is called
# The below represents seo_tracker/backend/.env
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=True, future=True)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

# Session initialised at module level 
async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


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
    async def get_rank_by_location(location, session: AsyncSession = Depends(get_session)):
        # Add logic

    Refer to page 57 Building Generative AI services with FastAPI
    """
    async with async_session() as session:
        yield session

# NOTE: Alembic is setup to handle database. 
# init_db no longer needed.
#async def init_db():
#    """
#    run_sync used as metadata.creat_all
#   doesn't execute asynchronously
#    """
#    async with engine.begin() as conn:
#        # await conn.run_sync(SQLModel.metadata.drop_all)
#        await conn.run_sync(SQLModel.metadata.create_all)