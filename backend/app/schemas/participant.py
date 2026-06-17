from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RosterMemberCreate(BaseModel):
    name: str = Field(..., min_length=1)


class RosterMemberUpdate(BaseModel):
    name: str = Field(..., min_length=1)


class RosterMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ParticipantCreate(BaseModel):
    name: str = Field(..., min_length=1)
    seed: Optional[int] = None
    type: str = "PLAYER"


class ParticipantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    seed: Optional[int] = None


class SeedOrder(BaseModel):
    # Participant ids in seed order (first = seed 1 = strongest).
    participant_ids: list[int]


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: Optional[int]
    name: str
    seed: Optional[int]
    type: str
    members: list[RosterMemberRead] = []
