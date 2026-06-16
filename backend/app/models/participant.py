from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id"), nullable=True, index=True
    )
    name = Column(String, nullable=False)
    seed = Column(Integer, nullable=True)  # lower = stronger; optional
    type = Column(String, default="PLAYER")  # "PLAYER" or "TEAM"

    # Roster members, only meaningful when type == "TEAM".
    members = relationship(
        "RosterMember",
        cascade="all, delete-orphan",
        order_by="RosterMember.id",
    )
