from .database import SessionLocal


def get_db():
    """
    This is so you can get the database for each endpoint function.
    Any endpoint that needs the database should have this as its last argument:

        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
