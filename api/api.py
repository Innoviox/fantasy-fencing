from fastapi import FastAPI
from .endpoints import fencers

api = FastAPI()

api.include_router(fencers.router, prefix="/fencers", tags=["users"])


@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

@api.get("/{id}")
async def get_fencer_by_id(id):
    ...