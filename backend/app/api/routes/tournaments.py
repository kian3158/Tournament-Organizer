from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.bracket import build_bracket_read
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.tournament import Tournament
from app.models.user import User
from app.schemas import (
    BracketRead,
    TournamentCreate,
    TournamentRead,
)
from app.services.bracket import BracketService
from app.services.exceptions import BracketError
from app.services.realtime import manager

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


def _get_tournament_or_404(db: Session, tournament_id: int) -> Tournament:
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


def _require_owner(tournament: Tournament, user: User) -> None:
    if tournament.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this tournament")


@router.post("", response_model=TournamentRead, status_code=status.HTTP_201_CREATED)
def create_tournament(
    payload: TournamentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.tournament.create(
        db, name=payload.name, format=payload.format, owner_id=current_user.id
    )


@router.get("", response_model=list[TournamentRead])
def list_tournaments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.tournament.list_for_owner(db, current_user.id)


@router.get("/{tournament_id}", response_model=TournamentRead)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    return _get_tournament_or_404(db, tournament_id)


@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tournament = _get_tournament_or_404(db, tournament_id)
    _require_owner(tournament, current_user)
    crud.tournament.delete(db, tournament)


@router.post("/{tournament_id}/generate", response_model=BracketRead)
async def generate_bracket(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tournament = _get_tournament_or_404(db, tournament_id)
    _require_owner(tournament, current_user)
    participants = crud.participant.list_for_tournament(db, tournament_id)
    try:
        BracketService().generate_bracket(db, tournament, participants)
    except BracketError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    db.commit()
    bracket = build_bracket_read(db, tournament_id)
    await manager.broadcast(tournament_id, bracket.model_dump(mode="json"))
    return bracket


@router.get("/{tournament_id}/bracket", response_model=BracketRead)
def get_bracket(tournament_id: int, db: Session = Depends(get_db)):
    _get_tournament_or_404(db, tournament_id)
    return build_bracket_read(db, tournament_id)
