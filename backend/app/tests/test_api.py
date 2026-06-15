"""End-to-end API tests exercising the full request flow (authenticated)."""

from app.tests.conftest import register_and_login


def create_tournament(client, headers, name="Cup"):
    r = client.post("/tournaments", json={"name": name}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def add_participant(client, headers, tid, name, seed=None):
    r = client.post(
        f"/tournaments/{tid}/participants",
        json={"name": name, "seed": seed},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_create_and_get_tournament(client, auth_headers):
    t = create_tournament(client, auth_headers)
    assert t["status"] == "DRAFT"
    assert t["format"] == "SINGLE_ELIM"

    # Reading a tournament is public (no auth needed).
    r = client.get(f"/tournaments/{t['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Cup"


def test_create_requires_auth(client):
    assert client.post("/tournaments", json={"name": "X"}).status_code == 401


def test_list_only_returns_own_tournaments(client, auth_headers):
    create_tournament(client, auth_headers, name="Mine")
    other_headers = register_and_login(client, email="other@example.com")
    create_tournament(client, other_headers, name="Theirs")

    mine = client.get("/tournaments", headers=auth_headers).json()
    assert [t["name"] for t in mine] == ["Mine"]


def test_get_missing_tournament_404(client):
    assert client.get("/tournaments/999").status_code == 404


def test_generate_requires_two_participants(client, auth_headers):
    t = create_tournament(client, auth_headers)
    add_participant(client, auth_headers, t["id"], "Solo")
    r = client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    assert r.status_code == 400


def test_non_owner_cannot_mutate(client, auth_headers):
    t = create_tournament(client, auth_headers)
    intruder = register_and_login(client, email="intruder@example.com")
    r = client.post(
        f"/tournaments/{t['id']}/participants",
        json={"name": "Sneaky"},
        headers=intruder,
    )
    assert r.status_code == 403


def test_full_flow_to_champion(client, auth_headers):
    t = create_tournament(client, auth_headers)
    tid = t["id"]
    for i in range(4):
        add_participant(client, auth_headers, tid, f"P{i}", seed=i + 1)

    r = client.post(f"/tournaments/{tid}/generate", headers=auth_headers)
    assert r.status_code == 200, r.text
    bracket = r.json()
    assert len(bracket["participants"]) == 4
    assert len(bracket["matches"]) == 3
    assert bracket["tournament"]["status"] == "ONGOING"

    while True:
        matches = client.get(f"/tournaments/{tid}/bracket").json()["matches"]
        playable = [
            m
            for m in matches
            if m["winner_id"] is None
            and m["player_a_id"] is not None
            and m["player_b_id"] is not None
        ]
        if not playable:
            break
        m = playable[0]
        resp = client.post(
            f"/matches/{m['id']}/result",
            json={"winner_id": m["player_a_id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text

    final = client.get(f"/tournaments/{tid}").json()
    assert final["status"] == "COMPLETED"


def test_report_result_on_unknown_match_404(client, auth_headers):
    r = client.post("/matches/4242/result", json={"winner_id": 1}, headers=auth_headers)
    assert r.status_code == 404
