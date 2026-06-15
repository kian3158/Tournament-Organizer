from typing import Optional

from .base import FormatStrategy, MatchPlan


def _next_power_of_two(n: int) -> int:
    """Smallest power of two >= n (for n >= 1)."""
    size = 1
    while size < n:
        size *= 2
    return size


def seed_slots(size: int) -> list[int]:
    """Standard single-elimination seeding order for a bracket of ``size``.

    Returns a list of 0-based seed indices in slot order, such that the top two
    seeds can only meet in the final, the top four only in the semis, etc.

    Example (size=8): [0, 7, 3, 4, 1, 6, 2, 5]
    -> first-round matches pair (0,7), (3,4), (1,6), (2,5).
    """
    order = [0]
    while len(order) < size:
        n = len(order) * 2
        nxt: list[int] = []
        for x in order:
            nxt.append(x)
            nxt.append(n - 1 - x)
        order = nxt
    return order


class SingleEliminationFormat(FormatStrategy):
    """Single-elimination bracket with standard seeding and byes.

    The bracket is padded up to the next power of two; the extra slots become
    byes that are handed to the strongest seeds. The caller (BracketService)
    is responsible for auto-advancing those byes once matches are persisted.
    """

    def build(self, participant_ids: list[int]) -> list[MatchPlan]:
        n = len(participant_ids)
        if n < 2:
            raise ValueError("A bracket needs at least 2 participants.")

        size = _next_power_of_two(n)
        slots = seed_slots(size)
        # Map each slot to a participant id, or None for a bye.
        players: list[Optional[int]] = [
            participant_ids[s] if s < n else None for s in slots
        ]

        plans: list[MatchPlan] = []
        idx = 0

        # Round 1: pair adjacent slots.
        prev_round: list[int] = []
        for i in range(0, size, 2):
            plans.append(
                MatchPlan(
                    index=idx,
                    round_number=1,
                    player_a=players[i],
                    player_b=players[i + 1],
                )
            )
            prev_round.append(idx)
            idx += 1

        # Subsequent rounds: empty matches fed by the previous round's winners.
        round_number = 2
        while len(prev_round) > 1:
            cur_round: list[int] = []
            for j in range(0, len(prev_round), 2):
                plan = MatchPlan(
                    index=idx,
                    round_number=round_number,
                    player_a=None,
                    player_b=None,
                )
                plans.append(plan)
                cur_round.append(idx)
                idx += 1

                # Wire the two feeder matches into this match's A/B slots.
                plans[prev_round[j]].next_index = plan.index
                plans[prev_round[j]].next_slot = "A"
                plans[prev_round[j + 1]].next_index = plan.index
                plans[prev_round[j + 1]].next_slot = "B"

            prev_round = cur_round
            round_number += 1

        return plans
