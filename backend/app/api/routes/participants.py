from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentStatus
from app.models.user import User
from app.schemas import (
    ParticipantCreate,
    ParticipantRead,
    ParticipantUpdate,
    RosterMemberCreate,
    RosterMemberRead,
    RosterMemberUpdate,
)

router = APIRouter(prefix="/tournaments/{tournament_id}", tags=["participants"])


def _owned_tournament(db: Session, tournament_id: int, user: User) -> Tournament:
    tournament = crud.tournament.get(db, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    if tournament.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this tournament")
    return tournament


def _editable(tournament: Tournament) -> None:
    if tournament.status != TournamentStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Participants can only be changed before the bracket is generated.",
        )


def _get_participant(
    db: Session, tournament_id: int, participant_id: int
) -> Participant:
    participant = crud.participant.get(db, participant_id)
    if participant is None or participant.tournament_id != tournament_id:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


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
    _owned_tournament(db, tournament_id, current_user)
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


@router.patch("/participants/{participant_id}", response_model=ParticipantRead)
def update_participant(
    tournament_id: int,
    participant_id: int,
    payload: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tournament = _owned_tournament(db, tournament_id, current_user)
    _editable(tournament)
    participant = _get_participant(db, tournament_id, participant_id)
    return crud.participant.update(
        db, participant, payload.model_dump(exclude_unset=True)
    )


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(
    tournament_id: int,
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tournament = _owned_tournament(db, tournament_id, current_user)
    _editable(tournament)
    participant = _get_participant(db, tournament_id, participant_id)
    crud.participant.delete(db, participant)


def _team_member(db: Session, tournament_id: int, participant_id: int, member_id: int):
    member = crud.roster_member.get(db, member_id)
    if member is None or member.participant_id != participant_id:
        raise HTTPException(status_code=404, detail="Roster member not found")
    return member


def _editable_team(
    db: Session, tournament_id: int, participant_id: int, user: User
) -> Participant:
    tournament = _owned_tournament(db, tournament_id, user)
    _editable(tournament)
    participant = _get_participant(db, tournament_id, participant_id)
    if participant.type != "TEAM":
        raise HTTPException(
            status_code=400, detail="Only team participants have a roster."
        )
    return participant


@router.post(
    "/participants/{participant_id}/members",
    response_model=RosterMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    tournament_id: int,
    participant_id: int,
    payload: RosterMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _editable_team(db, tournament_id, participant_id, current_user)
    return crud.roster_member.create(
        db, participant_id=participant_id, name=payload.name
    )


@router.patch(
    "/participants/{participant_id}/members/{member_id}",
    response_model=RosterMemberRead,
)
def update_member(
    tournament_id: int,
    participant_id: int,
    member_id: int,
    payload: RosterMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _editable_team(db, tournament_id, participant_id, current_user)
    member = _team_member(db, tournament_id, participant_id, member_id)
    return crud.roster_member.update(db, member, payload.name)


@router.delete(
    "/participants/{participant_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    tournament_id: int,
    participant_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _editable_team(db, tournament_id, participant_id, current_user)
    member = _team_member(db, tournament_id, participant_id, member_id)
    crud.roster_member.delete(db, member)
