from fastapi import APIRouter

from api.models.fencer import Fencer

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
