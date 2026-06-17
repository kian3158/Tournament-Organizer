from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.bracket import build_bracket_read
from app.db.session import get_db
from app.models.tournament import Tournament
from app.services.realtime import manager

router = APIRouter()


@router.websocket("/ws/tournaments/{tournament_id}")
async def tournament_bracket_socket(
    websocket: WebSocket,
    tournament_id: int,
    token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Live bracket feed for spectators. Requires the tournament's share token
    (browsers can't send auth headers on a WebSocket, so the owner passes the
    token too). Sends a snapshot on connect, then broadcasts on changes."""
    tournament = db.get(Tournament, tournament_id)
    if (
        tournament is None
        or not tournament.share_token
        or token != tournament.share_token
    ):
        await websocket.close(code=1008)
        return

    await manager.connect(tournament_id, websocket)
    try:
        bracket = build_bracket_read(db, tournament_id)
        if bracket is not None:
            await websocket.send_json(bracket.model_dump(mode="json"))
        # Keep the connection open; we don't expect inbound messages.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(tournament_id, websocket)
