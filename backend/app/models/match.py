from sqlalchemy import Column, Integer, ForeignKey, Enum
from .base import Base
import enum


class MatchSlot(str, enum.Enum):
    A = "A"
    B = "B"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    round_number = Column(Integer, nullable=False)
    player_a_id = Column(Integer, ForeignKey("participants.id"))
    player_b_id = Column(Integer, ForeignKey("participants.id"))
    winner_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    next_match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    next_match_slot = Column(Enum(MatchSlot), nullable=True)
