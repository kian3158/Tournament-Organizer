"""Tests for cross-tournament participant stats."""

from app.tests.conftest import register_and_login
from app.tests.test_editing import make, play_all


def test_two_player_stats(client, auth_headers):
    t, _ = make(client, auth_headers, players=2)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"][0]
    client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"]},
        headers=auth_headers,
    )

    stats = {s["name"]: s for s in client.get("/stats", headers=auth_headers).json()}
    assert stats["P0"]["wins"] == 1
    assert stats["P0"]["titles"] == 1
    assert stats["P0"]["played"] == 1
    assert stats["P1"]["losses"] == 1
    assert stats["P1"]["titles"] == 0


def test_stats_aggregate_totals(client, auth_headers):
    t, _ = make(client, auth_headers, players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    play_all(client, auth_headers, t["id"])

    stats = client.get("/stats", headers=auth_headers).json()
    assert len(stats) == 4
    assert all(s["tournaments"] == 1 for s in stats)
    # 4-player single elim plays 3 matches: 3 wins, 3 losses, 1 title in total.
    assert sum(s["wins"] for s in stats) == 3
    assert sum(s["losses"] for s in stats) == 3
    assert sum(s["titles"] for s in stats) == 1


def test_stats_scoped_to_owner(client, auth_headers):
    t, _ = make(client, auth_headers, players=2)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    play_all(client, auth_headers, t["id"])

    intruder = register_and_login(client, email="statsoutsider@example.com")
    assert client.get("/stats", headers=intruder).json() == []
