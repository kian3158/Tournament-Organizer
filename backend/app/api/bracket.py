from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models.tournament import TournamentFormat
from app.schemas import BracketRead, StandingRead
from app.services.standings import compute_standings

# Formats ranked by a standings table rather than a bracket tree.
_STANDINGS_FORMATS = {TournamentFormat.ROUND_ROBIN, TournamentFormat.SWISS}


def build_bracket_read(db: Session, tournament_id: int) -> Optional[BracketRead]:
    """Assemble the full bracket payload (tournament + participants + matches),
    including a standings table for standings-based formats."""
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        return None

    participants = crud.participant.list_for_tournament(db, tournament_id)
    matches = crud.match.list_for_tournament(db, tournament_id)

    standings = None
    if tournament.format in _STANDINGS_FORMATS:
        standings = [
            StandingRead.model_validate(row)
            for row in compute_standings(participants, matches)
        ]

    return BracketRead(
        tournament=tournament,
        participants=participants,
        matches=matches,
        standings=standings,
    )
