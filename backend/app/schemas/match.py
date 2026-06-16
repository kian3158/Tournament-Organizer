from typing import Optional

from pydantic import BaseModel, ConfigDict


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: int
    round_number: int
    player_a_id: Optional[int]
    player_b_id: Optional[int]
    winner_id: Optional[int]
    score_a: Optional[int]
    score_b: Optional[int]
    next_match_id: Optional[int]
    next_match_slot: Optional[str]
    bracket: Optional[str]
    loser_next_match_id: Optional[int]
    loser_next_match_slot: Optional[str]


class ResultReport(BaseModel):
    winner_id: int
    score_a: Optional[int] = None
    score_b: Optional[int] = None
