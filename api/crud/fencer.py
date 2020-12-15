from sqlalchemy.orm import Session

from api.schema.fencer import Fencer


def get_by_id(db: Session, id_num: int):
    return db.query(Fencer).filter(Fencer.id == id_num).first()
