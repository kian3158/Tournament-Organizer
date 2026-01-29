from sqlalchemy import Column, Integer, String
from .base import Base

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, default="PLAYER")  # could be TEAM later