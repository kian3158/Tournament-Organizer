from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.tournament import TournamentFormat, TournamentStatus

from .match import MatchRead
from .participant import ParticipantRead


class StandingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participant_id: int
    name: str
    played: int
    wins: int
    losses: int
    points: int


class TournamentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    format: TournamentFormat = TournamentFormat.SINGLE_ELIM
    best_of: int = 1
    third_place: bool = False

    @field_validator("best_of")
    @classmethod
    def _odd_and_positive(cls, v: int) -> int:
        if v < 1 or v % 2 == 0:
            raise ValueError("best_of must be a positive odd number (1, 3, 5, ...).")
        return v


class TournamentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: TournamentStatus
    format: TournamentFormat
    owner_id: int | None
    best_of: int
    third_place: bool
    share_token: str | None


class BracketRead(BaseModel):
    tournament: TournamentRead
    participants: list[ParticipantRead]
    matches: list[MatchRead]
    standings: Optional[list[StandingRead]] = None
