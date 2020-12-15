from sqlalchemy.orm import Session

from api import schema


def get_by_id(db: Session, id_num: int):
    return db.query(schema.fencer.Fencer)               \
             .filter(schema.fencer.Fencer.id == id_num) \
             .first()
