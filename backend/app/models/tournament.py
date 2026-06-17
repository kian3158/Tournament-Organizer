from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey
from .base import Base
import enum


class TournamentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"


class TournamentFormat(str, enum.Enum):
    SINGLE_ELIM = "SINGLE_ELIM"
    DOUBLE_ELIM = "DOUBLE_ELIM"
    ROUND_ROBIN = "ROUND_ROBIN"
    SWISS = "SWISS"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(Enum(TournamentStatus), default=TournamentStatus.DRAFT)
    format = Column(
        Enum(TournamentFormat),
        default=TournamentFormat.SINGLE_ELIM,
        nullable=False,
    )
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    # Games needed to win a match: 1, 3, 5, ... Winner needs (best_of+1)//2.
    best_of = Column(Integer, default=1, nullable=False)
    # Single elimination: add a match between the two semifinal losers.
    third_place = Column(Boolean, default=False, nullable=False)
