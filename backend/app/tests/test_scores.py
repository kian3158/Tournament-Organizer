"""Tests for optional per-match scores."""

from app.tests.test_editing import make


def first_match(client, headers, tid):
    return client.get(f"/tournaments/{tid}/bracket", headers=headers).json()["matches"][
        0
    ]


def test_report_with_scores(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    r = client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": 2, "score_b": 1},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["score_a"] == 2
    assert body["score_b"] == 1
    assert body["winner_id"] == m["player_a_id"]


def test_report_without_scores_leaves_them_null(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    r = client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"]},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["score_a"] is None
    assert r.json()["score_b"] is None


def test_score_winner_must_have_higher_score(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    r = client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": 1, "score_b": 2},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_score_tie_rejected(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    r = client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": 1, "score_b": 1},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_partial_score_rejected(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    r = client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": 2},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_correcting_winner_swaps_scores(client, auth_headers):
    t, _ = make(client, auth_headers, fmt="ROUND_ROBIN", players=3)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    m = first_match(client, auth_headers, t["id"])

    client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"], "score_a": 3, "score_b": 1},
        headers=auth_headers,
    )
    r = client.patch(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_b_id"]},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["winner_id"] == m["player_b_id"]
    # Scores follow the winner: player_b now holds the higher score.
    assert body["score_a"] == 1
    assert body["score_b"] == 3
