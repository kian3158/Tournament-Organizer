from typing import Optional

from sqlalchemy.orm import Session

from app.models.participant import Participant


def create(
    db: Session,
    *,
    tournament_id: int,
    name: str,
    seed: Optional[int] = None,
    type: str = "PLAYER",
) -> Participant:
    participant = Participant(
        tournament_id=tournament_id, name=name, seed=seed, type=type
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def list_for_tournament(db: Session, tournament_id: int) -> list[Participant]:
    return (
        db.query(Participant)
        .filter(Participant.tournament_id == tournament_id)
        .order_by(Participant.id)
        .all()
    )
