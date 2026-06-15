from sqlalchemy.orm import Session

from app.models.match import Match, MatchSlot
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus

from .exceptions import BracketError
from .formats import FormatStrategy, SingleEliminationFormat

# Format enum -> strategy. Only single-elimination is implemented in Phase 1;
# the others are wired in later phases.
_STRATEGIES: dict[TournamentFormat, type[FormatStrategy]] = {
    TournamentFormat.SINGLE_ELIM: SingleEliminationFormat,
}


class BracketService:
    """Generates and advances brackets, persisting state via the ORM session."""

    def _strategy_for(self, tournament: Tournament) -> FormatStrategy:
        strategy_cls = _STRATEGIES.get(tournament.format)
        if strategy_cls is None:
            raise BracketError(
                f"Format {tournament.format.value} is not supported yet."
            )
        return strategy_cls()

    def generate_bracket(
        self,
        db: Session,
        tournament: Tournament,
        participants: list[Participant],
    ) -> list[Match]:
        """Create all matches for a tournament and auto-advance any byes."""
        existing = db.query(Match).filter(Match.tournament_id == tournament.id).count()
        if existing:
            raise BracketError("Bracket has already been generated.")

        # Order participants by seed (strongest first); unseeded go last by id.
        ordered = sorted(
            participants, key=lambda p: (p.seed is None, p.seed or 0, p.id)
        )
        if len(ordered) < 2:
            raise BracketError("Need at least 2 participants to generate a bracket.")

        plans = self._strategy_for(tournament).build([p.id for p in ordered])

        # Create rows first, flush to assign ids, then wire next-match pointers.
        index_to_match: dict[int, Match] = {}
        for plan in plans:
            match = Match(
                tournament_id=tournament.id,
                round_number=plan.round_number,
                player_a_id=plan.player_a,
                player_b_id=plan.player_b,
            )
            db.add(match)
            index_to_match[plan.index] = match
        db.flush()

        for plan in plans:
            if plan.next_index is not None:
                match = index_to_match[plan.index]
                match.next_match_id = index_to_match[plan.next_index].id
                match.next_match_slot = MatchSlot(plan.next_slot)
        db.flush()

        # Auto-advance first-round byes (exactly one side present).
        for plan in plans:
            if plan.round_number != 1:
                continue
            a, b = plan.player_a, plan.player_b
            if (a is None) ^ (b is None):
                winner_id = a if a is not None else b
                self._record_winner(db, index_to_match[plan.index], winner_id)

        tournament.status = TournamentStatus.ONGOING
        db.flush()
        return list(index_to_match.values())

    def advance_match(self, db: Session, match_id: int, winner_id: int) -> Match:
        """Report the winner of a match and propagate them to the next round."""
        match = db.get(Match, match_id)
        if match is None:
            raise BracketError(f"Match {match_id} not found.")

        if match.player_a_id is None or match.player_b_id is None:
            raise BracketError("Match is not ready: both participants are not set.")
        if winner_id not in (match.player_a_id, match.player_b_id):
            raise BracketError("Winner must be one of the match participants.")
        if match.winner_id is not None:
            raise BracketError("Match result has already been reported.")

        self._record_winner(db, match, winner_id)

        # Reaching the final (no downstream match) completes the tournament.
        if match.next_match_id is None:
            tournament = db.get(Tournament, match.tournament_id)
            if tournament is not None:
                tournament.status = TournamentStatus.COMPLETED

        db.flush()
        return match

    def _record_winner(self, db: Session, match: Match, winner_id: int) -> None:
        """Set a match winner and place them into the downstream match slot."""
        match.winner_id = winner_id
        if match.next_match_id is None:
            return
        nxt = db.get(Match, match.next_match_id)
        if nxt is None:
            return
        if match.next_match_slot == MatchSlot.A:
            nxt.player_a_id = winner_id
        else:
            nxt.player_b_id = winner_id
