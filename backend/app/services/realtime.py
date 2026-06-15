from fastapi import WebSocket


class ConnectionManager:
    """Tracks live WebSocket connections grouped by tournament id.

    Used to push bracket updates to spectators. REST remains the source of
    truth for mutations; this is a read-only push channel.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}

    async def connect(self, tournament_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(tournament_id, set()).add(websocket)

    def disconnect(self, tournament_id: int, websocket: WebSocket) -> None:
        conns = self._connections.get(tournament_id)
        if conns is None:
            return
        conns.discard(websocket)
        if not conns:
            self._connections.pop(tournament_id, None)

    async def broadcast(self, tournament_id: int, message: dict) -> None:
        for websocket in list(self._connections.get(tournament_id, set())):
            try:
                await websocket.send_json(message)
            except Exception:
                # Drop connections that error out on send.
                self.disconnect(tournament_id, websocket)


manager = ConnectionManager()
