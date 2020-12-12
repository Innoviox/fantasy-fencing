from typing import List
from pydantic import BaseModel


class Fencer(BaseModel):
    id: int
    name: str

    victories: int
    victory_percentage: float

    touches_scored: List[int]
    touches_received: List[int]
    indicator: List[int]

    scores: List[List[int]]
    opponents: List[List[str]]
