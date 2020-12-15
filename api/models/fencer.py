from typing import List
from pydantic import BaseModel


class Fencer(BaseModel):
    id: int
    member_id: int
    name: str
    birthdate: int

    rating: str
    ranking: str

    matches: int
    wins: int

    class Config:
        orm_mode = True
