from pydantic import BaseModel


class ParticipantStat(BaseModel):
    name: str
    tournaments: int
    played: int
    wins: int
    losses: int
    titles: int
