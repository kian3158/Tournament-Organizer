from dataclasses import dataclass

from app.models.match import Match
from app.models.participant import Participant


@dataclass
class StandingRow:
    participant_id: int
    name: str
    played: int
    wins: int
    losses: int
    points: int  # one point per win


def compute_standings(
    participants: list[Participant], matches: list[Match]
) -> list[StandingRow]:
    """Build a ranking table from decided matches (for round robin / swiss).

    Ranked by wins (desc), then fewer losses, then name.
    """
    rows = {
        p.id: StandingRow(p.id, p.name, played=0, wins=0, losses=0, points=0)
        for p in participants
    }

    for match in matches:
        if match.winner_id is None:
            continue
        loser_id = (
            match.player_a_id
            if match.winner_id == match.player_b_id
            else match.player_b_id
        )
        if match.winner_id in rows:
            rows[match.winner_id].wins += 1
            rows[match.winner_id].points += 1
            rows[match.winner_id].played += 1
        if loser_id in rows:
            rows[loser_id].losses += 1
            rows[loser_id].played += 1

    return sorted(
        rows.values(),
        key=lambda r: (-r.wins, r.losses, r.name),
    )
