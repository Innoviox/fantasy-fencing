from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(fencers.router, prefix="/fencers", tags=["users"])
