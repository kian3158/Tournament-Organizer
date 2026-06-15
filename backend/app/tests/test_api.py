"""End-to-end API tests exercising the full request flow."""


def create_tournament(client, name="Cup"):
    r = client.post("/tournaments", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def add_participant(client, tid, name, seed=None):
    r = client.post(
        f"/tournaments/{tid}/participants",
        json={"name": name, "seed": seed},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_create_and_get_tournament(client):
    t = create_tournament(client)
    assert t["status"] == "DRAFT"
    assert t["format"] == "SINGLE_ELIM"

    r = client.get(f"/tournaments/{t['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Cup"


def test_get_missing_tournament_404(client):
    assert client.get("/tournaments/999").status_code == 404


def test_generate_requires_two_participants(client):
    t = create_tournament(client)
    add_participant(client, t["id"], "Solo")
    r = client.post(f"/tournaments/{t['id']}/generate")
    assert r.status_code == 400


def test_full_flow_to_champion(client):
    t = create_tournament(client)
    tid = t["id"]
    for i in range(4):
        add_participant(client, tid, f"P{i}", seed=i + 1)

    r = client.post(f"/tournaments/{tid}/generate")
    assert r.status_code == 200, r.text
    bracket = r.json()
    assert len(bracket["participants"]) == 4
    assert len(bracket["matches"]) == 3
    assert bracket["tournament"]["status"] == "ONGOING"

    # Play through every ready match until the bracket is finished.
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
        )
        assert resp.status_code == 200, resp.text

    final = client.get(f"/tournaments/{tid}").json()
    assert final["status"] == "COMPLETED"


def test_report_result_on_unknown_match_404(client):
    r = client.post("/matches/4242/result", json={"winner_id": 1})
    assert r.status_code == 404
