"""Tests for the double-elimination format (pure algorithm + service)."""

import pytest

from app.models.match import Match
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus
from app.services.bracket import BracketService
from app.services.formats.double_elimination import DoubleEliminationFormat


# --- pure algorithm ---


def build(n):
    return DoubleEliminationFormat().build(list(range(n)))


@pytest.mark.parametrize("n,expected", [(2, 3), (4, 7), (8, 15), (16, 31)])
def test_match_counts(n, expected):
    # winners (n-1) + losers (n-2) + grand final + reset == 2n - 1
    assert len(build(n)) == expected


@pytest.mark.parametrize("n", [3, 5, 6, 7, 9])
def test_non_power_of_two_builds_without_empty_losers_matches(n):
    plans = build(n)
    # Every losers-bracket match must have a real source for both slots, i.e.
    # something points a winner/loser into each slot (no orphaned empty match).
    lb_indexes = {p.index for p in plans if p.bracket == "LOSERS"}
    filled_a: set[int] = set()
    filled_b: set[int] = set()
    for p in plans:
        if p.next_index in lb_indexes:
            (filled_a if p.next_slot == "A" else filled_b).add(p.next_index)
        if p.loser_next_index in lb_indexes:
            (filled_a if p.loser_next_slot == "A" else filled_b).add(p.loser_next_index)
    for idx in lb_indexes:
        assert idx in filled_a and idx in filled_b


def test_all_brackets_present():
    labels = {p.bracket for p in build(8)}
    assert labels == {"WINNERS", "LOSERS", "GRAND_FINAL", "GRAND_FINAL_RESET"}


def test_winners_round1_losers_have_a_destination():
    wb1 = [p for p in build(8) if p.bracket == "WINNERS" and p.round_number == 1]
    assert len(wb1) == 4
    assert all(p.loser_next_index is not None for p in wb1)


def test_exactly_one_grand_final_and_reset():
    plans = build(8)
    assert sum(p.bracket == "GRAND_FINAL" for p in plans) == 1
    assert sum(p.bracket == "GRAND_FINAL_RESET" for p in plans) == 1


# --- service / persistence ---


def make_tournament(db, n):
    t = Tournament(name="DE", format=TournamentFormat.DOUBLE_ELIM)
    db.add(t)
    db.flush()
    for i in range(n):
        db.add(Participant(tournament_id=t.id, name=f"P{i}", seed=i + 1))
    db.commit()
    return t


def all_matches(db, tid):
    return (
        db.query(Match)
        .filter(Match.tournament_id == tid)
        .order_by(Match.round_number, Match.id)
        .all()
    )


def playable(db, tid):
    return [
        m
        for m in all_matches(db, tid)
        if m.winner_id is None
        and m.player_a_id is not None
        and m.player_b_id is not None
    ]


@pytest.mark.parametrize("n", [3, 5, 6, 7])
def test_non_power_of_two_completes(db, n):
    """Byes pad the bracket; playing every match still yields one champion."""
    t = make_tournament(db, n)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    guard = 0
    while playable(db, t.id):
        m = playable(db, t.id)[0]
        svc.advance_match(db, m.id, m.player_a_id)
        db.commit()
        guard += 1
        assert guard < 200

    db.refresh(t)
    assert t.status == TournamentStatus.COMPLETED


def test_losers_drop_into_losers_bracket(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    wb1 = [
        m
        for m in all_matches(db, t.id)
        if m.bracket == "WINNERS" and m.round_number == 1
    ]
    assert all(m.loser_next_match_id is not None for m in wb1)

    for m in wb1:
        svc.advance_match(db, m.id, m.player_a_id)
        db.commit()

    first_lb = next(
        m
        for m in all_matches(db, t.id)
        if m.bracket == "LOSERS" and m.round_number == 1
    )
    assert first_lb.player_a_id is not None
    assert first_lb.player_b_id is not None


@pytest.mark.parametrize("n", [2, 4, 8])
def test_completes_with_winners_champion(db, n):
    """Always picking player_a means the winners champion takes the grand
    final on the first try (no reset)."""
    t = make_tournament(db, n)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    guard = 0
    while playable(db, t.id):
        m = playable(db, t.id)[0]
        svc.advance_match(db, m.id, m.player_a_id)
        db.commit()
        guard += 1
        assert guard < 100

    db.refresh(t)
    assert t.status == TournamentStatus.COMPLETED
    reset = next(m for m in all_matches(db, t.id) if m.bracket == "GRAND_FINAL_RESET")
    assert reset.winner_id is None  # not needed when WB champ wins


def test_bracket_reset_when_losers_champion_wins(db):
    t = make_tournament(db, 4)
    svc = BracketService()
    svc.generate_bracket(db, t, db.query(Participant).all())
    db.commit()

    guard = 0
    while True:
        ready = playable(db, t.id)
        if not ready:
            break
        m = ready[0]
        if m.bracket == "GRAND_FINAL":
            # Losers champion (slot B) wins -> forces a reset match.
            svc.advance_match(db, m.id, m.player_b_id)
        else:
            svc.advance_match(db, m.id, m.player_a_id)
        db.commit()
        guard += 1
        assert guard < 100

    db.refresh(t)
    assert t.status == TournamentStatus.COMPLETED
    reset = next(m for m in all_matches(db, t.id) if m.bracket == "GRAND_FINAL_RESET")
    assert reset.player_a_id is not None and reset.player_b_id is not None
    assert reset.winner_id is not None  # reset was actually played
