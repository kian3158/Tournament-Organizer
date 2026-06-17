"""Tests for the swiss format (pure pairing + incremental rounds)."""

import pytest

from app.models.match import Match
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus
from app.services.bracket import BracketService
from app.services.formats.swiss import (
    SwissFormat,
    first_round_pairings,
    total_rounds,
)


# --- pure algorithm ---


@pytest.mark.parametrize("n,rounds", [(2, 1), (3, 2), (4, 2), (5, 3), (8, 3), (9, 4)])
def test_total_rounds(n, rounds):
    assert total_rounds(n) == rounds


def test_first_round_uses_fold_pairing():
    assert first_round_pairings([1, 2, 3, 4]) == [(1, 3), (2, 4)]
    assert first_round_pairings([1, 2, 3, 4, 5, 6, 7, 8]) == [
        (1, 5),
        (2, 6),
        (3, 7),
        (4, 8),
    ]


def test_first_round_odd_gives_bye_to_lowest_seed():
    assert first_round_pairings([1, 2, 3])[-1] == (3, None)


def test_next_round_avoids_rematches():
    played = {frozenset((1, 3)), frozenset((2, 4))}
    pairs = SwissFormat().next_round_pairings([1, 2, 3, 4], played, set())
    for a, b in pairs:
        if b is not None:
            assert frozenset((a, b)) not in played
    flat = sorted(x for pair in pairs for x in pair if x is not None)
    assert flat == [1, 2, 3, 4]


def test_next_round_bye_skips_players_who_had_one():
    pairs = SwissFormat().next_round_pairings([1, 2, 3], set(), {3})
    byes = [a for a, b in pairs if b is None]
    assert byes == [2]  # 3 already had a bye -> next lowest


# --- service / incremental rounds ---


def make_tournament(db, n):
    t = Tournament(name="Swiss", format=TournamentFormat.SWISS)
    db.add(t)
    db.flush()
    for i in range(n):
        db.add(Participant(tournament_id=t.id, name=f"P{i}", seed=i + 1))
    db.commit()
    return t


def swiss_matches(db, tid):
    return db.query(Match).filter(Match.tournament_id == tid).all()


def test_generate_creates_only_round_one(db):
    t = make_tournament(db, 8)
    BracketService().generate_bracket(db, t, db.query(Participant).all())
    db.commit()
    ms = swiss_matches(db, t.id)
    assert {m.round_number for m in ms} == {1}
    assert len(ms) == 4


def play_out(db, svc, tid):
    guard = 0
    while True:
        t = db.get(Tournament, tid)
        if t.status == TournamentStatus.COMPLETED:
            break
        pending = [
            m
            for m in swiss_matches(db, tid)
            if m.winner_id is None
            and m.player_a_id is not None
            and m.player_b_id is not None
        ]
        if not pending:
            break
        svc.advance_match(db, pending[0].id, pending[0].player_a_id)
        db.commit()
        guard += 1
        assert guard < 100


def test_next_round_is_generated_after_round_completes(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()
    assert {m.round_number for m in swiss_matches(db, t.id)} == {1}

    # Finish round 1.
    for m in [m for m in swiss_matches(db, t.id) if m.winner_id is None]:
        svc.advance_match(db, m.id, m.player_a_id)
        db.commit()

    assert {m.round_number for m in swiss_matches(db, t.id)} == {1, 2}


def test_full_run_completes_after_all_rounds(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    play_out(db, svc, t.id)

    db.refresh(t)
    assert t.status == TournamentStatus.COMPLETED
    assert max(m.round_number for m in swiss_matches(db, t.id)) == 2


def test_no_rematches_across_rounds(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()
    play_out(db, svc, t.id)

    pairs = [
        frozenset((m.player_a_id, m.player_b_id))
        for m in swiss_matches(db, t.id)
        if m.player_a_id is not None and m.player_b_id is not None
    ]
    assert len(pairs) == len(set(pairs))  # no pairing repeated


def test_standings_returned_for_swiss(client, auth_headers):
    t = client.post(
        "/tournaments",
        json={"name": "Swiss", "format": "SWISS"},
        headers=auth_headers,
    ).json()
    tid = t["id"]
    for i in range(4):
        client.post(
            f"/tournaments/{tid}/participants",
            json={"name": f"P{i}", "seed": i + 1},
            headers=auth_headers,
        )
    client.post(f"/tournaments/{tid}/generate", headers=auth_headers)

    # Play until no more ready matches (rounds appear as we go).
    for _ in range(50):
        ms = client.get(f"/tournaments/{tid}/bracket", headers=auth_headers).json()[
            "matches"
        ]
        ready = [
            m
            for m in ms
            if m["winner_id"] is None
            and m["player_a_id"] is not None
            and m["player_b_id"] is not None
        ]
        if not ready:
            break
        client.post(
            f"/matches/{ready[0]['id']}/result",
            json={"winner_id": ready[0]["player_a_id"]},
            headers=auth_headers,
        )

    bracket = client.get(f"/tournaments/{tid}/bracket", headers=auth_headers).json()
    assert bracket["tournament"]["status"] == "COMPLETED"
    assert bracket["standings"] is not None
    assert len(bracket["standings"]) == 4
