from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

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


class TournamentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: TournamentStatus
    format: TournamentFormat
    owner_id: int | None


class BracketRead(BaseModel):
    tournament: TournamentRead
    participants: list[ParticipantRead]
    matches: list[MatchRead]
    standings: Optional[list[StandingRead]] = None
