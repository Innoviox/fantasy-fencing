from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud
from api.models.fencer import Fencer
from api.utils import get_db

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@router.get("/{id}")
async def get_fencer_by_id(id_num: int, db: Session = Depends(get_db)):
    db_user = crud.fencer.get_by_id(db, user_id=id_num)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Fencer not found")
    return db_user
