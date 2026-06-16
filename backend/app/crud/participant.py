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


def get(db: Session, participant_id: int) -> Optional[Participant]:
    return db.get(Participant, participant_id)


def list_for_tournament(db: Session, tournament_id: int) -> list[Participant]:
    return (
        db.query(Participant)
        .filter(Participant.tournament_id == tournament_id)
        .order_by(Participant.id)
        .all()
    )


def update(db: Session, participant: Participant, fields: dict) -> Participant:
    if fields.get("name") is not None:
        participant.name = fields["name"]
    if "seed" in fields:
        participant.seed = fields["seed"]
    db.commit()
    db.refresh(participant)
    return participant


def delete(db: Session, participant: Participant) -> None:
    db.delete(participant)
    db.commit()
