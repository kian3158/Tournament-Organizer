from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import MatchRead, ResultReport
from app.services.bracket import BracketService
from app.services.exceptions import BracketError

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/{match_id}/result", response_model=MatchRead)
def report_result(
    match_id: int,
    payload: ResultReport,
    db: Session = Depends(get_db),
):
    try:
        match = BracketService().advance_match(db, match_id, payload.winner_id)
    except BracketError as exc:
        # "not found" is reported as 404, other invalid ops as 400.
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    db.commit()
    db.refresh(match)
    return match
