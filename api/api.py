from fastapi import FastAPI

from .endpoints import fencer

from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

api = FastAPI()

api.include_router(fencer.router, prefix="/fencer", tags=["users"])


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

