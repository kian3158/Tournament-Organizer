import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.participant import Participant
from app.models.roster_member import RosterMember
from app.models.tournament import Tournament, TournamentFormat


def create(
    db: Session,
    *,
    name: str,
    format: TournamentFormat,
    owner_id: Optional[int] = None,
    best_of: int = 1,
    third_place: bool = False,
) -> Tournament:
    tournament = Tournament(
        name=name,
        format=format,
        owner_id=owner_id,
        best_of=best_of,
        third_place=third_place,
        share_token=secrets.token_urlsafe(12),
    )
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament


def get(db: Session, tournament_id: int) -> Optional[Tournament]:
    return db.get(Tournament, tournament_id)


def list_for_owner(db: Session, owner_id: int) -> list[Tournament]:
    return (
        db.query(Tournament)
        .filter(Tournament.owner_id == owner_id)
        .order_by(Tournament.id)
        .all()
    )


def delete(db: Session, tournament: Tournament) -> None:
    """Delete a tournament along with its matches and participants."""
    db.query(Match).filter(Match.tournament_id == tournament.id).delete(
        synchronize_session=False
    )
    participant_ids = [
        pid
        for (pid,) in db.query(Participant.id).filter(
            Participant.tournament_id == tournament.id
        )
    ]
    if participant_ids:
        db.query(RosterMember).filter(
            RosterMember.participant_id.in_(participant_ids)
        ).delete(synchronize_session=False)
    db.query(Participant).filter(Participant.tournament_id == tournament.id).delete(
        synchronize_session=False
    )
    db.delete(tournament)
    db.commit()
