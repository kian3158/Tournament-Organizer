"""Tests for editing/deleting participants and tournaments, and correcting
match results."""

from app.tests.conftest import register_and_login


def make(client, headers, fmt="SINGLE_ELIM", players=0, name="T"):
    t = client.post(
        "/tournaments", json={"name": name, "format": fmt}, headers=headers
    ).json()
    ids = []
    for i in range(players):
        p = client.post(
            f"/tournaments/{t['id']}/participants",
            json={"name": f"P{i}", "seed": i + 1},
            headers=headers,
        ).json()
        ids.append(p["id"])
    return t, ids


def play_all(client, headers, tid):
    for _ in range(100):
        ms = client.get(f"/tournaments/{tid}/bracket").json()["matches"]
        ready = [
            m
            for m in ms
            if m["winner_id"] is None
            and m["player_a_id"] is not None
            and m["player_b_id"] is not None
        ]
        if not ready:
            return
        client.post(
            f"/matches/{ready[0]['id']}/result",
            json={"winner_id": ready[0]["player_a_id"]},
            headers=headers,
        )


# --- participants ---


def test_rename_participant(client, auth_headers):
    t, ids = make(client, auth_headers, players=2)
    r = client.patch(
        f"/tournaments/{t['id']}/participants/{ids[0]}",
        json={"name": "Renamed"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


def test_delete_participant(client, auth_headers):
    t, ids = make(client, auth_headers, players=2)
    r = client.delete(
        f"/tournaments/{t['id']}/participants/{ids[0]}", headers=auth_headers
    )
    assert r.status_code == 204
    remaining = client.get(f"/tournaments/{t['id']}/participants").json()
    assert len(remaining) == 1


def test_cannot_edit_participants_after_generate(client, auth_headers):
    t, ids = make(client, auth_headers, players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    assert (
        client.delete(
            f"/tournaments/{t['id']}/participants/{ids[0]}", headers=auth_headers
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/tournaments/{t['id']}/participants/{ids[0]}",
            json={"name": "X"},
            headers=auth_headers,
        ).status_code
        == 400
    )


def test_non_owner_cannot_edit_participant(client, auth_headers):
    t, ids = make(client, auth_headers, players=2)
    intruder = register_and_login(client, email="intruder@example.com")
    assert (
        client.delete(
            f"/tournaments/{t['id']}/participants/{ids[0]}", headers=intruder
        ).status_code
        == 403
    )


# --- tournament deletion ---


def test_delete_tournament(client, auth_headers):
    t, _ = make(client, auth_headers, players=2)
    assert (
        client.delete(f"/tournaments/{t['id']}", headers=auth_headers).status_code
        == 204
    )
    assert client.get(f"/tournaments/{t['id']}").status_code == 404


def test_non_owner_cannot_delete_tournament(client, auth_headers):
    t, _ = make(client, auth_headers)
    intruder = register_and_login(client, email="x@example.com")
    assert client.delete(f"/tournaments/{t['id']}", headers=intruder).status_code == 403


# --- correcting results ---


def test_correct_result_repropagates(client, auth_headers):
    t, ids = make(client, auth_headers, players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    ms = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"]
    r1 = next(m for m in ms if m["round_number"] == 1)

    client.post(
        f"/matches/{r1['id']}/result",
        json={"winner_id": r1["player_a_id"]},
        headers=auth_headers,
    )
    r = client.patch(
        f"/matches/{r1['id']}/result",
        json={"winner_id": r1["player_b_id"]},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["winner_id"] == r1["player_b_id"]

    ms2 = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"]
    final = next(m for m in ms2 if m["next_match_id"] is None)
    assert r1["player_b_id"] in (final["player_a_id"], final["player_b_id"])
    assert r1["player_a_id"] not in (final["player_a_id"], final["player_b_id"])


def test_correct_blocked_when_downstream_decided(client, auth_headers):
    t, ids = make(client, auth_headers, players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    play_all(client, auth_headers, t["id"])

    ms = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"]
    r1 = next(m for m in ms if m["round_number"] == 1)
    r = client.patch(
        f"/matches/{r1['id']}/result",
        json={"winner_id": r1["player_b_id"]},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_correct_result_round_robin(client, auth_headers):
    t, ids = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"][0]
    client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"]},
        headers=auth_headers,
    )
    r = client.patch(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_b_id"]},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["winner_id"] == m["player_b_id"]


def test_cannot_correct_grand_final(client, auth_headers):
    t, ids = make(client, auth_headers, fmt="DOUBLE_ELIM", players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    play_all(client, auth_headers, t["id"])

    ms = client.get(f"/tournaments/{t['id']}/bracket").json()["matches"]
    gf = next(m for m in ms if m["bracket"] == "GRAND_FINAL")
    other = (
        gf["player_b_id"] if gf["winner_id"] == gf["player_a_id"] else gf["player_a_id"]
    )
    r = client.patch(
        f"/matches/{gf['id']}/result",
        json={"winner_id": other},
        headers=auth_headers,
    )
    assert r.status_code == 400
