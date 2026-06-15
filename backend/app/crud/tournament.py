from typing import Optional

from sqlalchemy.orm import Session

from app.models.tournament import Tournament, TournamentFormat


def create(db: Session, *, name: str, format: TournamentFormat) -> Tournament:
    tournament = Tournament(name=name, format=format)
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament


def get(db: Session, tournament_id: int) -> Optional[Tournament]:
    return db.get(Tournament, tournament_id)


def list_all(db: Session) -> list[Tournament]:
    return db.query(Tournament).order_by(Tournament.id).all()
