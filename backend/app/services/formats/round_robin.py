from .base import Bracket, FormatStrategy, MatchPlan


class RoundRobinFormat(FormatStrategy):
    """Round robin: every participant plays every other once.

    Matches are scheduled into rounds with the circle method so that, within a
    round, each participant appears at most once. With an odd number of
    participants one player sits out each round (no match is created for the
    bye). There is no bracket tree — ranking comes from the standings table.
    """

    def build(self, participant_ids: list[int]) -> list[MatchPlan]:
        n = len(participant_ids)
        if n < 2:
            raise ValueError("A round robin needs at least 2 participants.")

        # Circle method: pad with a None "bye" slot when the count is odd.
        ring: list[int | None] = list(participant_ids)
        if n % 2 == 1:
            ring.append(None)

        size = len(ring)
        rounds = size - 1
        half = size // 2

        plans: list[MatchPlan] = []
        for r in range(rounds):
            for i in range(half):
                a = ring[i]
                b = ring[size - 1 - i]
                if a is not None and b is not None:
                    plans.append(
                        MatchPlan(
                            index=len(plans),
                            round_number=r + 1,
                            player_a=a,
                            player_b=b,
                            bracket=Bracket.ROUND_ROBIN,
                        )
                    )
            # Rotate everyone except the first entry (standard circle method).
            ring = [ring[0], ring[-1]] + ring[1:-1]

        return plans
