from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.match import Match
from app.models.tournament import TournamentFormat, TournamentStatus
from app.models.user import User
from app.schemas import ParticipantStat

router = APIRouter(prefix="/stats", tags=["stats"])


def _champion_id(participants, matches, fmt):
    """Best-effort champion of a completed tournament."""
    if fmt in (TournamentFormat.SINGLE_ELIM, TournamentFormat.DOUBLE_ELIM):
        for label in ("GRAND_FINAL_RESET", "GRAND_FINAL"):
            m = next((m for m in matches if m.bracket == label and m.winner_id), None)
            if m:
                return m.winner_id
        final = next(
            (
                m
                for m in matches
                if m.bracket is None
                and m.next_match_id is None
                and m.winner_id is not None
            ),
            None,
        )
        return final.winner_id if final else None
    # Round robin / swiss: the most wins.
    wins: dict[int, int] = defaultdict(int)
    for m in matches:
        if m.winner_id is not None:
            wins[m.winner_id] += 1
    return max(wins, key=lambda k: wins[k]) if wins else None


@router.get("", response_model=list[ParticipantStat])
def my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate results by participant name across the user's tournaments."""
    rows: dict[str, dict[str, int]] = defaultdict(
        lambda: {"tournaments": 0, "played": 0, "wins": 0, "losses": 0, "titles": 0}
    )

    for tournament in crud.tournament.list_for_owner(db, current_user.id):
        participants = crud.participant.list_for_tournament(db, tournament.id)
        id_to_name = {p.id: p.name for p in participants}
        matches = db.query(Match).filter(Match.tournament_id == tournament.id).all()

        for name in {p.name for p in participants}:
            rows[name]["tournaments"] += 1

        for m in matches:
            if m.winner_id is None or m.player_a_id is None or m.player_b_id is None:
                continue  # skip unplayed matches and byes
            loser_id = m.player_a_id if m.winner_id == m.player_b_id else m.player_b_id
            if (winner := id_to_name.get(m.winner_id)) is not None:
                rows[winner]["wins"] += 1
                rows[winner]["played"] += 1
            if (loser := id_to_name.get(loser_id)) is not None:
                rows[loser]["losses"] += 1
                rows[loser]["played"] += 1

        if tournament.status == TournamentStatus.COMPLETED:
            champ = id_to_name.get(
                _champion_id(participants, matches, tournament.format)
            )
            if champ is not None:
                rows[champ]["titles"] += 1

    stats = [ParticipantStat(name=name, **vals) for name, vals in rows.items()]
    stats.sort(key=lambda s: (-s.wins, s.losses, s.name))
    return stats
