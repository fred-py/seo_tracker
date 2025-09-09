from fastapi import FastAPI
from .core.db import init_db
from .models import Location, OrganicRank

app = FastAPI()

# Initialise/create database
#init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}