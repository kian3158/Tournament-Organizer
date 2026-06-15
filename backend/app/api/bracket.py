from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.schemas import BracketRead


def build_bracket_read(db: Session, tournament_id: int) -> Optional[BracketRead]:
    """Assemble the full bracket payload (tournament + participants + matches)."""
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        return None
    return BracketRead(
        tournament=tournament,
        participants=crud.participant.list_for_tournament(db, tournament_id),
        matches=crud.match.list_for_tournament(db, tournament_id),
    )
