from sqlalchemy.orm import Session

from app.models.match import Match


def list_for_tournament(db: Session, tournament_id: int) -> list[Match]:
    return (
        db.query(Match)
        .filter(Match.tournament_id == tournament_id)
        .order_by(Match.round_number, Match.id)
        .all()
    )
