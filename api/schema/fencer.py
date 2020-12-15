from ..database import Base

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Fencer(Base):
    __tablename__ = "fencers"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, index=True)
    name = Column(String)
    birthdate = Column(String)

    rating = Column(String)
    ranking = Column(String, default='')

    matches = Column(Integer, default=0)
    wins = Column(Integer, default=0)