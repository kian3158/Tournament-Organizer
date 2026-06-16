from typing import Optional

from sqlalchemy.orm import Session

from app.models.roster_member import RosterMember


def create(db: Session, *, participant_id: int, name: str) -> RosterMember:
    member = RosterMember(participant_id=participant_id, name=name)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get(db: Session, member_id: int) -> Optional[RosterMember]:
    return db.get(RosterMember, member_id)


def update(db: Session, member: RosterMember, name: str) -> RosterMember:
    member.name = name
    db.commit()
    db.refresh(member)
    return member


def delete(db: Session, member: RosterMember) -> None:
    db.delete(member)
    db.commit()
