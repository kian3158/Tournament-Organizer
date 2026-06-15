"""Unit tests for the pure single-elimination bracket algorithm (no DB)."""

import math

import pytest

from app.services.formats.single_elimination import (
    SingleEliminationFormat,
    seed_slots,
)


def build(n):
    """Build a bracket for participant ids 0..n-1 (ids == seed order)."""
    return SingleEliminationFormat().build(list(range(n)))


def test_seed_slots_known_orders():
    assert seed_slots(2) == [0, 1]
    assert seed_slots(4) == [0, 3, 1, 2]
    assert seed_slots(8) == [0, 7, 3, 4, 1, 6, 2, 5]


def test_seed_slots_is_a_permutation():
    for size in (2, 4, 8, 16, 32):
        assert sorted(seed_slots(size)) == list(range(size))


@pytest.mark.parametrize("n", [2, 4, 8, 16])
def test_power_of_two_has_no_byes(n):
    plans = build(n)
    # N-1 total matches, expected number of rounds.
    assert len(plans) == n - 1
    assert max(p.round_number for p in plans) == int(math.log2(n))

    first_round = [p for p in plans if p.round_number == 1]
    assert len(first_round) == n // 2
    # No byes: every first-round slot is filled.
    for p in first_round:
        assert p.player_a is not None and p.player_b is not None


@pytest.mark.parametrize("n", [2, 4, 5, 8, 13, 16])
def test_match_count_and_single_final(n):
    plans = build(n)
    size = 1
    while size < n:
        size *= 2
    assert len(plans) == size - 1
    finals = [p for p in plans if p.next_index is None]
    assert len(finals) == 1
    assert finals[0].round_number == int(math.log2(size))


@pytest.mark.parametrize(
    "n,expected_byes",
    [(3, 1), (5, 3), (6, 2), (7, 1), (9, 7), (12, 4)],
)
def test_byes_count_and_go_to_top_seeds(n, expected_byes):
    plans = build(n)
    first_round = [p for p in plans if p.round_number == 1]

    bye_matches = [
        p for p in first_round if (p.player_a is None) ^ (p.player_b is None)
    ]
    assert len(bye_matches) == expected_byes
    # No match should ever have two byes.
    assert not any(p.player_a is None and p.player_b is None for p in first_round)

    # The strongest `expected_byes` seeds (ids 0..byes-1) each receive a bye.
    bye_recipients = {
        (p.player_a if p.player_a is not None else p.player_b) for p in bye_matches
    }
    assert bye_recipients == set(range(expected_byes))


@pytest.mark.parametrize("n", [4, 8, 16])
def test_top_two_seeds_only_meet_in_final(n):
    """Seed 0 and seed 1 must start in opposite halves of the bracket."""
    plans = build(n)
    first_round = sorted(
        [p for p in plans if p.round_number == 1], key=lambda p: p.index
    )
    half = len(first_round) // 2

    def half_of(seed):
        for i, p in enumerate(first_round):
            if p.player_a == seed or p.player_b == seed:
                return 0 if i < half else 1
        raise AssertionError("seed not found")

    assert half_of(0) != half_of(1)


def test_every_non_final_match_points_to_a_valid_next():
    plans = build(8)
    by_index = {p.index: p for p in plans}
    for p in plans:
        if p.next_index is not None:
            assert p.next_index in by_index
            assert p.next_slot in ("A", "B")
            # Winner advances to a later round.
            assert by_index[p.next_index].round_number == p.round_number + 1


@pytest.mark.parametrize("n", [0, 1])
def test_too_few_participants_raises(n):
    with pytest.raises(ValueError):
        build(n)
