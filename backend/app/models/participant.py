from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id"), nullable=True, index=True
    )
    name = Column(String, nullable=False)
    seed = Column(Integer, nullable=True)  # lower = stronger; optional
    type = Column(String, default="PLAYER")  # could be TEAM later
