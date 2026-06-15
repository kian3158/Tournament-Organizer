"""Tests for the live bracket WebSocket feed."""


def setup_bracket(client, headers, players=2):
    t = client.post("/tournaments", json={"name": "WS"}, headers=headers).json()
    tid = t["id"]
    for i in range(players):
        client.post(
            f"/tournaments/{tid}/participants",
            json={"name": f"P{i}", "seed": i + 1},
            headers=headers,
        )
    client.post(f"/tournaments/{tid}/generate", headers=headers)
    return tid


def test_ws_sends_snapshot_on_connect(client, auth_headers):
    tid = setup_bracket(client, auth_headers)
    with client.websocket_connect(f"/ws/tournaments/{tid}") as ws:
        msg = ws.receive_json()
        assert msg["tournament"]["id"] == tid
        assert len(msg["matches"]) == 1
        assert len(msg["participants"]) == 2


def test_ws_broadcasts_on_result(client, auth_headers):
    tid = setup_bracket(client, auth_headers)
    with client.websocket_connect(f"/ws/tournaments/{tid}") as ws:
        ws.receive_json()  # drain the initial snapshot

        match = client.get(f"/tournaments/{tid}/bracket").json()["matches"][0]
        client.post(
            f"/matches/{match['id']}/result",
            json={"winner_id": match["player_a_id"]},
            headers=auth_headers,
        )

        update = ws.receive_json()
        assert update["matches"][0]["winner_id"] == match["player_a_id"]
        assert update["tournament"]["status"] == "COMPLETED"
