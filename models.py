from pydantic import BaseModel

class Fencer(BaseModel):
    name: str
    victories: int
    victories_over_matches: float
    touches_scored: int
    touches_received: int
    indicator: int