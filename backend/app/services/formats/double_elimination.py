from typing import Callable, Optional

from .base import Bracket, FormatStrategy, MatchPlan
from .single_elimination import seed_slots

# A "source" links a not-yet-created downstream match into the slot that this
# entrant will arrive in. ``None`` means the entrant doesn't exist (a bye), so
# whatever it would have played simply passes the opponent through.
Source = Optional[Callable[[int, str], None]]


class DoubleEliminationFormat(FormatStrategy):
    """Double elimination: a winners bracket, a losers bracket, and a grand
    final with a possible bracket reset.

    A player is eliminated only after two losses. Losers of the winners bracket
    drop into the losers bracket; the losers-bracket champion meets the
    winners-bracket champion in the grand final. If the losers-bracket champion
    wins (handing the winners champion their first loss), a reset match decides
    the title.

    Non-power-of-two counts are padded up to the next power of two; the extra
    winners-bracket slots become byes. A bye produces no loser, so the losers
    bracket simply passes the lone dropper through instead of creating an empty
    match.
    """

    def build(self, participant_ids: list[int]) -> list[MatchPlan]:
        n = len(participant_ids)
        if n < 2:
            raise ValueError("A bracket needs at least 2 participants.")

        size = 1
        while size < n:
            size *= 2
        k = size.bit_length() - 1  # number of winners-bracket rounds
        players: list[Optional[int]] = [
            participant_ids[s] if s < n else None for s in seed_slots(size)
        ]
        plans: list[MatchPlan] = []

        def add(round_number: int, bracket: str, a=None, b=None) -> MatchPlan:
            plan = MatchPlan(
                index=len(plans),
                round_number=round_number,
                player_a=a,
                player_b=b,
                bracket=bracket,
            )
            plans.append(plan)
            return plan

        wb_rounds = _build_winners_bracket(add, plans, players, size, k)
        lb_champion = _build_losers_bracket(add, plans, wb_rounds, k)
        _build_grand_final(add, plans, wb_rounds[-1][0], lb_champion, k)
        return plans


def _build_winners_bracket(add, plans, players, size, k) -> list[list[int]]:
    rounds: list[list[int]] = []
    first = [
        add(1, Bracket.WINNERS, players[i], players[i + 1]).index
        for i in range(0, size, 2)
    ]
    rounds.append(first)
    for r in range(2, k + 1):
        prev = rounds[-1]
        cur: list[int] = []
        for m in range(0, len(prev), 2):
            nxt = add(r, Bracket.WINNERS)
            cur.append(nxt.index)
            _link_winner(plans[prev[m]], nxt.index, "A")
            _link_winner(plans[prev[m + 1]], nxt.index, "B")
        rounds.append(cur)
    return rounds


def _build_losers_bracket(add, plans, wb_rounds, k):
    """Build the losers bracket; return the index of its final match (or None)."""
    if k < 2:
        return None

    last_match: dict[str, Optional[int]] = {"idx": None}
    round_no = 1

    def combine(s1: Source, s2: Source) -> Source:
        """Merge two entrant sources into one survivor source.

        With both present, a real match is created. With one missing (a bye),
        the present entrant passes straight through. With neither, nothing
        survives.
        """
        if s1 is None:
            return s2
        if s2 is None:
            return s1
        lb = add(round_no, Bracket.LOSERS)
        s1(lb.index, "A")
        s2(lb.index, "B")
        last_match["idx"] = lb.index
        return _winner_source(plans, lb.index)

    # Minor round 1: pair up the losers dropping from winners round 1.
    sources = [_loser_source(plans, idx) for idx in wb_rounds[0]]
    sources = [combine(sources[i], sources[i + 1]) for i in range(0, len(sources), 2)]
    round_no += 1

    for i in range(1, k):
        # Major round: survivors meet the losers dropping from winners round i+1.
        drops = [_loser_source(plans, idx) for idx in wb_rounds[i]]
        sources = [combine(sources[m], drops[m]) for m in range(len(sources))]
        round_no += 1

        # Minor round: pair up the major-round survivors (when more than one).
        if len(sources) > 1:
            sources = [
                combine(sources[j], sources[j + 1]) for j in range(0, len(sources), 2)
            ]
            round_no += 1

    return last_match["idx"]


def _build_grand_final(add, plans, wb_final, lb_champion, k) -> None:
    grand_final = add(k + 1, Bracket.GRAND_FINAL)
    _link_winner(plans[wb_final], grand_final.index, "A")
    if lb_champion is not None:
        _link_winner(plans[lb_champion], grand_final.index, "B")
    else:
        # 2 players: the winners-final loser is the losers champion.
        _link_loser(plans[wb_final], grand_final.index, "B")

    # Reset match: populated only if the losers champion wins the grand final.
    add(k + 2, Bracket.GRAND_FINAL_RESET)


def _loser_source(plans, idx) -> Source:
    plan = plans[idx]
    # A winners round-1 bye has an empty slot and contributes no loser.
    if plan.round_number == 1 and (plan.player_a is None or plan.player_b is None):
        return None
    return lambda target, slot: _link_loser(plan, target, slot)


def _winner_source(plans, idx) -> Source:
    plan = plans[idx]
    return lambda target, slot: _link_winner(plan, target, slot)


def _link_winner(plan: MatchPlan, next_index: int, slot: str) -> None:
    plan.next_index = next_index
    plan.next_slot = slot


def _link_loser(plan: MatchPlan, next_index: int, slot: str) -> None:
    plan.loser_next_index = next_index
    plan.loser_next_slot = slot
