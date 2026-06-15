from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api.bracket import build_bracket_read
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.match import Match
from app.models.user import User
from app.schemas import MatchRead, ResultReport
from app.services.bracket import BracketService
from app.services.exceptions import BracketError
from app.services.realtime import manager

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/{match_id}/result", response_model=MatchRead)
async def report_result(
    match_id: int,
    payload: ResultReport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership is checked against the match's tournament before mutating.
    match = db.get(Match, match_id)
    if match is not None:
        tournament = crud.tournament.get(db, match.tournament_id)
        if tournament is not None and tournament.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You do not own this tournament"
            )

    try:
        match = BracketService().advance_match(db, match_id, payload.winner_id)
    except BracketError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    db.commit()
    db.refresh(match)

    bracket = build_bracket_read(db, match.tournament_id)
    if bracket is not None:
        await manager.broadcast(match.tournament_id, bracket.model_dump(mode="json"))
    return match
