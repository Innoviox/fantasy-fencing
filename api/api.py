from fastapi import FastAPI

from .endpoints import fencer
from .database import engine, Base

Base.metadata.create_all(bind=engine)  # set up the database

api = FastAPI()

# put the fencer endpoints at /fencer/
api.include_router(fencer.router, prefix="/fencer", tags=["users"])


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
