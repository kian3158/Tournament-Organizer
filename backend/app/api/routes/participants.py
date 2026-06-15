from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas import ParticipantCreate, ParticipantRead

router = APIRouter(prefix="/tournaments/{tournament_id}", tags=["participants"])


@router.post(
    "/participants",
    response_model=ParticipantRead,
    status_code=status.HTTP_201_CREATED,
)
def add_participant(
    tournament_id: int,
    payload: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    if tournament.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this tournament")
    return crud.participant.create(
        db,
        tournament_id=tournament_id,
        name=payload.name,
        seed=payload.seed,
        type=payload.type,
    )


@router.get("/participants", response_model=list[ParticipantRead])
def list_participants(tournament_id: int, db: Session = Depends(get_db)):
    if crud.tournament.get(db, tournament_id) is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return crud.participant.list_for_tournament(db, tournament_id)
