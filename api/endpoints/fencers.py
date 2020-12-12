from fastapi import APIRouter

from api.models.fencer import Fencer

router = APIRouter()

@router.get("/")