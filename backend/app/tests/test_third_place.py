"""Tests for the optional single-elimination third-place match."""


def make(client, headers, players=4, third=True, fmt="SINGLE_ELIM"):
    t = client.post(
        "/tournaments",
        json={"name": "TP", "format": fmt, "third_place": third},
        headers=headers,
    ).json()
    for i in range(players):
        client.post(
            f"/tournaments/{t['id']}/participants",
            json={"name": f"P{i}", "seed": i + 1},
            headers=headers,
        )
    client.post(f"/tournaments/{t['id']}/generate", headers=headers)
    return t


def matches(client, headers, tid):
    return client.get(f"/tournaments/{tid}/bracket", headers=headers).json()["matches"]


def semis(client, headers, tid):
    return [
        m
        for m in matches(client, headers, tid)
        if m["round_number"] == 1 and m["bracket"] is None
    ]


def report(client, headers, m):
    client.post(
        f"/matches/{m['id']}/result",
        json={"winner_id": m["player_a_id"]},
        headers=headers,
    )


def test_third_place_match_created(client, auth_headers):
    t = make(client, auth_headers, players=4)
    tp = [
        m
        for m in matches(client, auth_headers, t["id"])
        if m["bracket"] == "THIRD_PLACE"
    ]
    assert len(tp) == 1


def test_no_third_place_when_disabled(client, auth_headers):
    t = make(client, auth_headers, players=4, third=False)
    assert not any(
        m["bracket"] == "THIRD_PLACE" for m in matches(client, auth_headers, t["id"])
    )


def test_no_third_place_for_round_robin(client, auth_headers):
    t = make(client, auth_headers, players=4, fmt="ROUND_ROBIN")
    assert not any(
        m["bracket"] == "THIRD_PLACE" for m in matches(client, auth_headers, t["id"])
    )


def test_no_third_place_with_two_players(client, auth_headers):
    t = make(client, auth_headers, players=2)
    assert not any(
        m["bracket"] == "THIRD_PLACE" for m in matches(client, auth_headers, t["id"])
    )


def test_semifinal_losers_feed_third_place(client, auth_headers):
    t = make(client, auth_headers, players=4)
    for m in semis(client, auth_headers, t["id"]):
        report(client, auth_headers, m)
    tp = next(
        m
        for m in matches(client, auth_headers, t["id"])
        if m["bracket"] == "THIRD_PLACE"
    )
    assert tp["player_a_id"] is not None and tp["player_b_id"] is not None


def test_third_place_does_not_complete_tournament(client, auth_headers):
    t = make(client, auth_headers, players=4)
    for m in semis(client, auth_headers, t["id"]):
        report(client, auth_headers, m)

    tp = next(
        m
        for m in matches(client, auth_headers, t["id"])
        if m["bracket"] == "THIRD_PLACE"
    )
    report(client, auth_headers, tp)  # play third place before the final
    assert (
        client.get(f"/tournaments/{t['id']}", headers=auth_headers).json()["status"]
        == "ONGOING"
    )

    final = next(
        m
        for m in matches(client, auth_headers, t["id"])
        if m["bracket"] is None and m["next_match_id"] is None
    )
    report(client, auth_headers, final)
    assert (
        client.get(f"/tournaments/{t['id']}", headers=auth_headers).json()["status"]
        == "COMPLETED"
    )
