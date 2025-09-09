from sqlmodel import Session, SQLModel, create_engine, select

#from app import crud
#from app.core.config import settings
from app.models import Location, Keyword, OrganicRank
from dotenv import load_dotenv
import os

load_dotenv()

postgress = os.getenv('DATABASE_URL')
engine = create_engine(postgress, echo=True)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
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