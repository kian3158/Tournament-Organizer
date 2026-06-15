"""Tests for BracketService persistence and advancement (against a DB)."""

import pytest

from app.models.match import Match
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus
from app.services.bracket import BracketService
from app.services.exceptions import BracketError


def make_tournament(db, n, *, seeded=True):
    """Create a tournament with n seeded participants; return (tournament, ids)."""
    tournament = Tournament(name="Test", format=TournamentFormat.SINGLE_ELIM)
    db.add(tournament)
    db.flush()
    ids = []
    for i in range(n):
        p = Participant(
            tournament_id=tournament.id,
            name=f"P{i}",
            seed=(i + 1) if seeded else None,
        )
        db.add(p)
        db.flush()
        ids.append(p.id)
    db.commit()
    return tournament, ids


def matches(db, tournament_id):
    return (
        db.query(Match)
        .filter(Match.tournament_id == tournament_id)
        .order_by(Match.round_number, Match.id)
        .all()
    )


def test_generate_persists_matches_and_sets_status(db):
    tournament, ids = make_tournament(db, 4)
    BracketService().generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()

    ms = matches(db, tournament.id)
    assert len(ms) == 3  # 4 players -> 3 matches
    assert tournament.status == TournamentStatus.ONGOING

    round1 = [m for m in ms if m.round_number == 1]
    final = [m for m in ms if m.round_number == 2]
    assert len(round1) == 2 and len(final) == 1
    # Final starts empty; round 1 fully populated.
    assert final[0].player_a_id is None and final[0].player_b_id is None
    for m in round1:
        assert m.player_a_id is not None and m.player_b_id is not None
        assert m.next_match_id == final[0].id


def test_bye_auto_advances_top_seed(db):
    tournament, ids = make_tournament(db, 3)  # size 4 -> 1 bye for seed 1
    BracketService().generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()

    ms = matches(db, tournament.id)
    assert len(ms) == 3
    # The top seed (first id) should already be advanced into the final.
    final = next(m for m in ms if m.next_match_id is None)
    assert ids[0] in (final.player_a_id, final.player_b_id)
    # Exactly one round-1 match was auto-decided (the bye).
    decided = [m for m in ms if m.round_number == 1 and m.winner_id is not None]
    assert len(decided) == 1
    assert decided[0].winner_id == ids[0]


def test_generate_twice_raises(db):
    tournament, _ = make_tournament(db, 4)
    service = BracketService()
    service.generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()
    with pytest.raises(BracketError):
        service.generate_bracket(db, tournament, db.query(Participant).all())


def test_generate_with_one_participant_raises(db):
    tournament, _ = make_tournament(db, 1)
    with pytest.raises(BracketError):
        BracketService().generate_bracket(db, tournament, db.query(Participant).all())


def test_full_run_to_champion(db):
    tournament, ids = make_tournament(db, 4)
    service = BracketService()
    service.generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()

    # Win every match by always picking player_a; play until the final resolves.
    while True:
        playable = [
            m
            for m in matches(db, tournament.id)
            if m.winner_id is None
            and m.player_a_id is not None
            and m.player_b_id is not None
        ]
        if not playable:
            break
        m = playable[0]
        service.advance_match(db, m.id, m.player_a_id)
        db.commit()

    db.refresh(tournament)
    assert tournament.status == TournamentStatus.COMPLETED
    final = next(m for m in matches(db, tournament.id) if m.next_match_id is None)
    assert final.winner_id is not None


def test_advance_rejects_unready_match(db):
    tournament, ids = make_tournament(db, 4)
    service = BracketService()
    service.generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()
    final = next(m for m in matches(db, tournament.id) if m.next_match_id is None)
    with pytest.raises(BracketError):
        service.advance_match(db, final.id, ids[0])


def test_advance_rejects_non_participant_winner(db):
    tournament, ids = make_tournament(db, 4)
    service = BracketService()
    service.generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()
    m = next(
        x
        for x in matches(db, tournament.id)
        if x.player_a_id and x.player_b_id and x.winner_id is None
    )
    with pytest.raises(BracketError):
        service.advance_match(db, m.id, 99999)


def test_advance_rejects_double_report(db):
    tournament, ids = make_tournament(db, 4)
    service = BracketService()
    service.generate_bracket(db, tournament, db.query(Participant).all())
    db.commit()
    m = next(
        x
        for x in matches(db, tournament.id)
        if x.player_a_id and x.player_b_id and x.winner_id is None
    )
    service.advance_match(db, m.id, m.player_a_id)
    db.commit()
    with pytest.raises(BracketError):
        service.advance_match(db, m.id, m.player_b_id)


def test_advance_unknown_match_raises(db):
    with pytest.raises(BracketError):
        BracketService().advance_match(db, 123456, 1)
