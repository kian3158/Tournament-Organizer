from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from .base import Base
import enum

class TournamentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(Enum(TournamentStatus), default=TournamentStatus.DRAFT)
    owner_id = Column(Integer, nullable=True)  # for future User support