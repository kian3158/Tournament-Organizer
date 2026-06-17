"""Tests for the tournament-level best-of-N setting."""


def make_bo(client, headers, best_of, fmt="ROUND_ROBIN", players=3):
    t = client.post(
        "/tournaments",
        json={"name": "BO", "format": fmt, "best_of": best_of},
        headers=headers,
    )
    if t.status_code != 201:
        return t, None
    tid = t.json()["id"]
    for i in range(players):
        client.post(
            f"/tournaments/{tid}/participants",
            json={"name": f"P{i}"},
            headers=headers,
        )
    client.post(f"/tournaments/{tid}/generate", headers=headers)
    return t, tid


def first_match(client, headers, tid):
    return client.get(f"/tournaments/{tid}/bracket", headers=headers).json()["matches"][
        0
    ]


def report(client, headers, m, a, b):
    return client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": a, "score_b": b},
        headers=headers,
    )


def test_best_of_stored_on_create(client, auth_headers):
    t, _ = make_bo(client, auth_headers, 5)
    assert t.json()["best_of"] == 5


def test_even_best_of_rejected(client, auth_headers):
    t, _ = make_bo(client, auth_headers, 4)
    assert t.status_code == 422


def test_bo3_clinching_score_ok(client, auth_headers):
    _, tid = make_bo(client, auth_headers, 3)
    m = first_match(client, auth_headers, tid)
    r = report(client, auth_headers, m, 2, 1)  # winner reaches 2 of 3
    assert r.status_code == 200, r.text
    assert r.json()["score_a"] == 2


def test_bo3_sweep_ok(client, auth_headers):
    _, tid = make_bo(client, auth_headers, 3)
    m = first_match(client, auth_headers, tid)
    assert report(client, auth_headers, m, 2, 0).status_code == 200


def test_bo3_winner_short_of_majority_rejected(client, auth_headers):
    _, tid = make_bo(client, auth_headers, 3)
    m = first_match(client, auth_headers, tid)
    assert report(client, auth_headers, m, 1, 0).status_code == 400


def test_bo3_winner_over_majority_rejected(client, auth_headers):
    _, tid = make_bo(client, auth_headers, 3)
    m = first_match(client, auth_headers, tid)
    assert report(client, auth_headers, m, 3, 1).status_code == 400


def test_bo1_allows_free_scores(client, auth_headers):
    _, tid = make_bo(client, auth_headers, 1)
    m = first_match(client, auth_headers, tid)
    # best_of 1 keeps the loose rule: winner just needs the higher score.
    assert report(client, auth_headers, m, 2, 1).status_code == 200
