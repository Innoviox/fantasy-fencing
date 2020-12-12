from fastapi import FastAPI
from .endpoints import fencers

api = FastAPI()

api.include_router(fencers.router, prefix="/fencers", tags=["users"])


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

