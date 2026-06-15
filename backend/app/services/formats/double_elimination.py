from .base import Bracket, FormatStrategy, MatchPlan
from .single_elimination import seed_slots


class DoubleEliminationFormat(FormatStrategy):
    """Double elimination: a winners bracket, a losers bracket, and a grand
    final with a possible bracket reset.

    A player is eliminated only after two losses. Losers of the winners bracket
    drop into the losers bracket; the losers-bracket champion meets the
    winners-bracket champion in the grand final. If the losers-bracket champion
    wins (handing the winners champion their first loss), a reset match decides
    the title.

    Note: currently requires a power-of-two participant count. Byes for other
    counts are tracked in the backlog.
    """

    def build(self, participant_ids: list[int]) -> list[MatchPlan]:
        n = len(participant_ids)
        if n < 2:
            raise ValueError("A bracket needs at least 2 participants.")
        if n & (n - 1) != 0:
            raise ValueError(
                "Double elimination currently requires a power-of-two "
                "number of participants (2, 4, 8, 16, ...)."
            )

        size = n
        k = size.bit_length() - 1  # number of winners-bracket rounds
        players = [participant_ids[s] for s in seed_slots(size)]
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
    """Returns the index of the losers-bracket final, or None when k == 1."""
    if k < 2:
        return None

    round_no = 1
    # First minor round: losers of winners round 1, paired up.
    prev = []
    wb1 = wb_rounds[0]
    for m in range(0, len(wb1), 2):
        lb = add(round_no, Bracket.LOSERS)
        prev.append(lb.index)
        _link_loser(plans[wb1[m]], lb.index, "A")
        _link_loser(plans[wb1[m + 1]], lb.index, "B")
    round_no += 1

    for i in range(1, k):
        # Major round: previous LB winners vs losers of winners round i + 1.
        wb_drop = wb_rounds[i]
        major = []
        for m in range(len(prev)):
            lb = add(round_no, Bracket.LOSERS)
            major.append(lb.index)
            _link_winner(plans[prev[m]], lb.index, "A")
            _link_loser(plans[wb_drop[m]], lb.index, "B")
        round_no += 1
        prev = major

        # Minor round: pair up the major-round winners (when more than one).
        if len(prev) > 1:
            minor = []
            for m in range(0, len(prev), 2):
                lb = add(round_no, Bracket.LOSERS)
                minor.append(lb.index)
                _link_winner(plans[prev[m]], lb.index, "A")
                _link_winner(plans[prev[m + 1]], lb.index, "B")
            round_no += 1
            prev = minor

    return prev[0]


def _build_grand_final(add, plans, wb_final, lb_champion, k) -> None:
    grand_final = add(k + 1, Bracket.GRAND_FINAL)
    _link_winner(plans[wb_final], grand_final.index, "A")
    if k >= 2:
        _link_winner(plans[lb_champion], grand_final.index, "B")
    else:
        # 2 players: the winners-final loser is the losers champion.
        _link_loser(plans[wb_final], grand_final.index, "B")

    # Reset match: populated only if the losers champion wins the grand final.
    add(k + 2, Bracket.GRAND_FINAL_RESET)


def _link_winner(plan: MatchPlan, next_index: int, slot: str) -> None:
    plan.next_index = next_index
    plan.next_slot = slot


def _link_loser(plan: MatchPlan, next_index: int, slot: str) -> None:
    plan.loser_next_index = next_index
    plan.loser_next_slot = slot
