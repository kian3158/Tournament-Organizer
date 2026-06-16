from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class Bracket:
    """String labels stored on Match.bracket to distinguish formats/sections."""

    WINNERS = "WINNERS"
    LOSERS = "LOSERS"
    GRAND_FINAL = "GRAND_FINAL"
    GRAND_FINAL_RESET = "GRAND_FINAL_RESET"
    ROUND_ROBIN = "ROUND_ROBIN"
    SWISS = "SWISS"
    THIRD_PLACE = "THIRD_PLACE"


@dataclass
class MatchPlan:
    """A DB-agnostic description of a single match in a generated bracket.

    ``index`` is a local identifier within one bracket build. ``next_index``
    points at the match the winner advances into (resolved to real DB ids when
    persisted), and ``next_slot`` is which side ("A"/"B") the winner fills.

    For double elimination, ``loser_next_index``/``loser_next_slot`` route the
    loser into the losers bracket, and ``bracket`` labels which bracket the
    match belongs to.

    A ``None`` player represents a bye in the first round.
    """

    index: int
    round_number: int
    player_a: Optional[int]
    player_b: Optional[int]
    next_index: Optional[int] = None
    next_slot: Optional[str] = None
    loser_next_index: Optional[int] = None
    loser_next_slot: Optional[str] = None
    bracket: Optional[str] = None


class FormatStrategy(ABC):
    """Interface every tournament format implements.

    Kept free of any database or HTTP concerns so the bracket math can be unit
    tested in isolation. See docs/ARCHITECTURE.md.
    """

    @abstractmethod
    def build(self, participant_ids: list[int]) -> list[MatchPlan]:
        """Return the full set of matches for the given participants.

        ``participant_ids`` must already be ordered by seed (strongest first).
        """
        raise NotImplementedError
