from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.schemas import (
    BracketRead,
    TournamentCreate,
    TournamentRead,
)
from app.services.bracket import BracketService
from app.services.exceptions import BracketError

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


def _get_tournament_or_404(db: Session, tournament_id: int):
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("", response_model=TournamentRead, status_code=status.HTTP_201_CREATED)
def create_tournament(payload: TournamentCreate, db: Session = Depends(get_db)):
    return crud.tournament.create(db, name=payload.name, format=payload.format)


@router.get("", response_model=list[TournamentRead])
def list_tournaments(db: Session = Depends(get_db)):
    return crud.tournament.list_all(db)


@router.get("/{tournament_id}", response_model=TournamentRead)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    return _get_tournament_or_404(db, tournament_id)


@router.post("/{tournament_id}/generate", response_model=BracketRead)
def generate_bracket(tournament_id: int, db: Session = Depends(get_db)):
    tournament = _get_tournament_or_404(db, tournament_id)
    participants = crud.participant.list_for_tournament(db, tournament_id)
    try:
        BracketService().generate_bracket(db, tournament, participants)
    except BracketError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    db.commit()
    return _build_bracket(db, tournament_id)


@router.get("/{tournament_id}/bracket", response_model=BracketRead)
def get_bracket(tournament_id: int, db: Session = Depends(get_db)):
    _get_tournament_or_404(db, tournament_id)
    return _build_bracket(db, tournament_id)


def _build_bracket(db: Session, tournament_id: int) -> BracketRead:
    tournament = _get_tournament_or_404(db, tournament_id)
    return BracketRead(
        tournament=tournament,
        participants=crud.participant.list_for_tournament(db, tournament_id),
        matches=crud.match.list_for_tournament(db, tournament_id),
    )
