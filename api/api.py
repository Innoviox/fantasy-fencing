from fastapi import FastAPI

from .endpoints import fencers

from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

api = FastAPI()

api.include_router(fencers.router, prefix="/fencers", tags=["users"])

'''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# , db: Session = Depends(get_db)
'''

@api.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

