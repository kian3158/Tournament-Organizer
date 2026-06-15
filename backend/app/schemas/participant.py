from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ParticipantCreate(BaseModel):
    name: str = Field(..., min_length=1)
    seed: Optional[int] = None
    type: str = "PLAYER"


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: Optional[int]
    name: str
    seed: Optional[int]
    type: str
