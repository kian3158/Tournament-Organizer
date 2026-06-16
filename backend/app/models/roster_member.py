from sqlalchemy import Column, ForeignKey, Integer, String

from .base import Base


class RosterMember(Base):
    __tablename__ = "roster_members"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(
        Integer, ForeignKey("participants.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)
