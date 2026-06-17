"""Tests for the round-robin format (pure algorithm, service, standings)."""

from itertools import combinations

import pytest

from app.models.match import Match
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus
from app.services.bracket import BracketService
from app.services.formats.round_robin import RoundRobinFormat


# --- pure algorithm ---


def build(n):
    return RoundRobinFormat().build(list(range(n)))


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 8])
def test_match_count_is_n_choose_2(n):
    assert len(build(n)) == n * (n - 1) // 2


def test_every_pair_plays_exactly_once():
    plans = build(5)
    pairs = {frozenset((p.player_a, p.player_b)) for p in plans}
    assert pairs == {frozenset(c) for c in combinations(range(5), 2)}
    assert len(pairs) == len(plans)


@pytest.mark.parametrize("n", [4, 5, 6])
def test_no_participant_appears_twice_in_a_round(n):
    plans = build(n)
    per_round: dict[int, list[int]] = {}
    for p in plans:
        per_round.setdefault(p.round_number, []).extend([p.player_a, p.player_b])
    for players in per_round.values():
        assert len(players) == len(set(players))


def test_rejects_too_few_participants():
    with pytest.raises(ValueError):
        build(1)


# --- service ---


def make_tournament(db, n):
    t = Tournament(name="RR", format=TournamentFormat.ROUND_ROBIN)
    db.add(t)
    db.flush()
    for i in range(n):
        db.add(Participant(tournament_id=t.id, name=f"P{i}", seed=i + 1))
    db.commit()
    return t


def matches(db, tid):
    return db.query(Match).filter(Match.tournament_id == tid).all()


def test_generate_and_play_to_completion(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    assert len(matches(db, t.id)) == 6
    db.refresh(t)
    assert t.status == TournamentStatus.ONGOING

    guard = 0
    while True:
        pending = [m for m in matches(db, t.id) if m.winner_id is None]
        if not pending:
            break
        svc.advance_match(db, pending[0].id, pending[0].player_a_id)
        db.commit()
        guard += 1
        assert guard < 50

    db.refresh(t)
    assert t.status == TournamentStatus.COMPLETED


def test_one_result_does_not_complete_tournament(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()
    first = matches(db, t.id)[0]
    svc.advance_match(db, first.id, first.player_a_id)
    db.commit()
    db.refresh(t)
    assert t.status == TournamentStatus.ONGOING


# --- standings (via API) ---


def test_standings_returned_for_round_robin(client, auth_headers):
    t = client.post(
        "/tournaments",
        json={"name": "RR", "format": "ROUND_ROBIN"},
        headers=auth_headers,
    ).json()
    tid = t["id"]
    for i in range(3):
        client.post(
            f"/tournaments/{tid}/participants",
            json={"name": f"P{i}", "seed": i + 1},
            headers=auth_headers,
        )
    client.post(f"/tournaments/{tid}/generate", headers=auth_headers)

    ms = client.get(f"/tournaments/{tid}/bracket", headers=auth_headers).json()[
        "matches"
    ]
    for m in ms:
        client.post(
            f"/matches/{m['id']}/result",
            json={"winner_id": m["player_a_id"]},
            headers=auth_headers,
        )

    bracket = client.get(f"/tournaments/{tid}/bracket", headers=auth_headers).json()
    standings = bracket["standings"]
    assert standings is not None
    assert len(standings) == 3
    # 3 matches played -> 3 wins distributed in total.
    assert sum(row["wins"] for row in standings) == 3
    # Sorted by points descending.
    points = [row["points"] for row in standings]
    assert points == sorted(points, reverse=True)


def test_standings_absent_for_single_elimination(client, auth_headers):
    t = client.post("/tournaments", json={"name": "SE"}, headers=auth_headers).json()
    bracket = client.get(f"/tournaments/{t['id']}/bracket", headers=auth_headers).json()
    assert bracket["standings"] is None
