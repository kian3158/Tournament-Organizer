from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.bracket import build_bracket_read
from app.db.session import get_db
from app.services.realtime import manager

router = APIRouter()


@router.websocket("/ws/tournaments/{tournament_id}")
async def tournament_bracket_socket(
    websocket: WebSocket,
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """Live bracket feed for spectators. Sends a snapshot on connect, then
    receives broadcast updates whenever the bracket changes."""
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
