from typing import Optional

from sqlalchemy.orm import Session

from app.models.match import Match, MatchSlot
from app.models.participant import Participant
from app.models.tournament import Tournament, TournamentFormat, TournamentStatus

from .exceptions import BracketError
from .formats import (
    Bracket,
    DoubleEliminationFormat,
    FormatStrategy,
    RoundRobinFormat,
    SingleEliminationFormat,
    SwissFormat,
    total_rounds,
)

# Format enum -> strategy.
_STRATEGIES: dict[TournamentFormat, type[FormatStrategy]] = {
    TournamentFormat.SINGLE_ELIM: SingleEliminationFormat,
    TournamentFormat.DOUBLE_ELIM: DoubleEliminationFormat,
    TournamentFormat.ROUND_ROBIN: RoundRobinFormat,
    TournamentFormat.SWISS: SwissFormat,
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

        try:
            plans = self._strategy_for(tournament).build([p.id for p in ordered])
        except ValueError as exc:
            raise BracketError(str(exc))

        index_to_match = self._create_matches(db, tournament, plans)
        self._wire_pointers(plans, index_to_match)
        db.flush()
        self._auto_advance_byes(db, plans, index_to_match)

        tournament.status = TournamentStatus.ONGOING
        db.flush()
        return list(index_to_match.values())

    def _create_matches(
        self, db: Session, tournament: Tournament, plans
    ) -> dict[int, Match]:
        index_to_match: dict[int, Match] = {}
        for plan in plans:
            match = Match(
                tournament_id=tournament.id,
                round_number=plan.round_number,
                player_a_id=plan.player_a,
                player_b_id=plan.player_b,
                bracket=plan.bracket,
            )
            db.add(match)
            index_to_match[plan.index] = match
        db.flush()
        return index_to_match

    def _wire_pointers(self, plans, index_to_match: dict[int, Match]) -> None:
        for plan in plans:
            match = index_to_match[plan.index]
            if plan.next_index is not None:
                match.next_match_id = index_to_match[plan.next_index].id
                match.next_match_slot = MatchSlot(plan.next_slot)
            if plan.loser_next_index is not None:
                match.loser_next_match_id = index_to_match[plan.loser_next_index].id
                match.loser_next_match_slot = MatchSlot(plan.loser_next_slot)

    def _auto_advance_byes(
        self, db: Session, plans, index_to_match: dict[int, Match]
    ) -> None:
        """Auto-resolve first-round byes (exactly one side present)."""
        for plan in plans:
            if plan.round_number != 1:
                continue
            a, b = plan.player_a, plan.player_b
            if (a is None) ^ (b is None):
                winner_id = a if a is not None else b
                self._record_winner(db, index_to_match[plan.index], winner_id)

    def advance_match(
        self,
        db: Session,
        match_id: int,
        winner_id: int,
        score_a: Optional[int] = None,
        score_b: Optional[int] = None,
    ) -> Match:
        """Report the winner of a match and propagate the result."""
        match = db.get(Match, match_id)
        if match is None:
            raise BracketError(f"Match {match_id} not found.")

        if match.player_a_id is None or match.player_b_id is None:
            raise BracketError("Match is not ready: both participants are not set.")
        if winner_id not in (match.player_a_id, match.player_b_id):
            raise BracketError("Winner must be one of the match participants.")
        if match.winner_id is not None:
            raise BracketError("Match result has already been reported.")

        self._set_scores(match, winner_id, score_a, score_b, self._best_of(db, match))
        self._record_winner(db, match, winner_id)
        # Flush so completion checks (which query the DB) see this result;
        # the session uses autoflush=False.
        db.flush()
        self._handle_completion(db, match, winner_id)

        db.flush()
        return match

    def correct_match(
        self,
        db: Session,
        match_id: int,
        new_winner_id: int,
        score_a: Optional[int] = None,
        score_b: Optional[int] = None,
    ) -> Match:
        """Change an already-reported result, when it's safe to do so."""
        match = db.get(Match, match_id)
        if match is None:
            raise BracketError(f"Match {match_id} not found.")
        if new_winner_id == match.winner_id:
            return match  # no change

        self._assert_correctable(db, match, new_winner_id)

        self._clear_propagation(db, match)
        match.winner_id = None
        db.flush()
        self._record_winner(db, match, new_winner_id)

        if score_a is not None or score_b is not None:
            self._set_scores(
                match, new_winner_id, score_a, score_b, self._best_of(db, match)
            )
        elif match.score_a is not None and match.score_b is not None:
            # Flipping the winner flips which side has the higher score.
            match.score_a, match.score_b = match.score_b, match.score_a

        db.flush()
        return match

    def _assert_correctable(
        self, db: Session, match: Match, new_winner_id: int
    ) -> None:
        """Raise BracketError unless this result can be safely changed."""
        if match.winner_id is None:
            raise BracketError("Match has no result to correct yet.")
        if new_winner_id not in (match.player_a_id, match.player_b_id):
            raise BracketError("Winner must be one of the match participants.")
        if match.bracket in (Bracket.GRAND_FINAL, Bracket.GRAND_FINAL_RESET):
            raise BracketError("Grand final results can't be corrected.")

        # Refuse if a downstream match that depends on this one is already decided.
        for next_id in (match.next_match_id, match.loser_next_match_id):
            if next_id is None:
                continue
            downstream = db.get(Match, next_id)
            if downstream is not None and downstream.winner_id is not None:
                raise BracketError(
                    "A later match that depends on this result is already "
                    "decided. Correct that one first."
                )

        # Swiss generates rounds from results, so don't change a locked-in round.
        if match.bracket == Bracket.SWISS:
            later_rounds = (
                db.query(Match)
                .filter(
                    Match.tournament_id == match.tournament_id,
                    Match.bracket == Bracket.SWISS,
                    Match.round_number > match.round_number,
                )
                .count()
            )
            if later_rounds:
                raise BracketError(
                    "Later swiss rounds already exist; correct results in the "
                    "current round only."
                )

    def _clear_propagation(self, db: Session, match: Match) -> None:
        """Remove this match's previously-propagated players from downstream."""
        old_winner = match.winner_id
        old_loser = (
            match.player_a_id if old_winner == match.player_b_id else match.player_b_id
        )

        if match.next_match_id is not None:
            nxt = db.get(Match, match.next_match_id)
            if nxt is not None:
                if (
                    match.next_match_slot == MatchSlot.A
                    and nxt.player_a_id == old_winner
                ):
                    nxt.player_a_id = None
                elif (
                    match.next_match_slot == MatchSlot.B
                    and nxt.player_b_id == old_winner
                ):
                    nxt.player_b_id = None

        if match.loser_next_match_id is not None and old_loser is not None:
            lnxt = db.get(Match, match.loser_next_match_id)
            if lnxt is not None:
                if (
                    match.loser_next_match_slot == MatchSlot.A
                    and lnxt.player_a_id == old_loser
                ):
                    lnxt.player_a_id = None
                elif (
                    match.loser_next_match_slot == MatchSlot.B
                    and lnxt.player_b_id == old_loser
                ):
                    lnxt.player_b_id = None

    def _best_of(self, db: Session, match: Match) -> int:
        tournament = db.get(Tournament, match.tournament_id)
        return tournament.best_of if tournament is not None else 1

    def _set_scores(
        self,
        match: Match,
        winner_id: int,
        score_a: Optional[int],
        score_b: Optional[int],
        best_of: int = 1,
    ) -> None:
        """Validate and store optional per-match scores."""
        if score_a is None and score_b is None:
            return
        if score_a is None or score_b is None:
            raise BracketError("Enter a score for both players, or neither.")
        if score_a < 0 or score_b < 0:
            raise BracketError("Scores can't be negative.")
        if score_a == score_b:
            raise BracketError(
                "A match can't end in a tie; the winner needs the higher score."
            )
        winner_score = score_a if winner_id == match.player_a_id else score_b
        loser_score = score_b if winner_id == match.player_a_id else score_a
        if winner_score < loser_score:
            raise BracketError("The winner must have the higher score.")
        if best_of > 1:
            needed = (best_of + 1) // 2
            if winner_score != needed:
                raise BracketError(
                    f"Best of {best_of}: the winner needs exactly {needed} games."
                )
            if loser_score >= needed:
                raise BracketError(
                    f"Best of {best_of}: the loser can't reach {needed} games."
                )
        match.score_a = score_a
        match.score_b = score_b

    def _record_winner(self, db: Session, match: Match, winner_id: int) -> None:
        """Set the winner and route winner (and loser, if any) downstream."""
        match.winner_id = winner_id

        if match.next_match_id is not None:
            nxt = db.get(Match, match.next_match_id)
            if nxt is not None:
                if match.next_match_slot == MatchSlot.A:
                    nxt.player_a_id = winner_id
                else:
                    nxt.player_b_id = winner_id

        if match.loser_next_match_id is not None:
            loser_id = (
                match.player_a_id
                if winner_id == match.player_b_id
                else match.player_b_id
            )
            if loser_id is not None:
                lnxt = db.get(Match, match.loser_next_match_id)
                if lnxt is not None:
                    if match.loser_next_match_slot == MatchSlot.A:
                        lnxt.player_a_id = loser_id
                    else:
                        lnxt.player_b_id = loser_id

    def _handle_completion(self, db: Session, match: Match, winner_id: int) -> None:
        """Mark the tournament complete (or trigger a grand-final reset)."""
        tournament = db.get(Tournament, match.tournament_id)
        if tournament is None:
            return

        if match.bracket == Bracket.GRAND_FINAL:
            # player_a is the winners champion; if they win, they're undefeated.
            if winner_id == match.player_a_id:
                tournament.status = TournamentStatus.COMPLETED
            else:
                # Losers champion won — both now have one loss; play the reset.
                reset = (
                    db.query(Match)
                    .filter(
                        Match.tournament_id == match.tournament_id,
                        Match.bracket == Bracket.GRAND_FINAL_RESET,
                    )
                    .first()
                )
                if reset is not None:
                    reset.player_a_id = match.player_a_id
                    reset.player_b_id = match.player_b_id
        elif match.bracket == Bracket.GRAND_FINAL_RESET:
            tournament.status = TournamentStatus.COMPLETED
        elif match.bracket == Bracket.ROUND_ROBIN:
            # Complete once every scheduled match has a result.
            remaining = (
                db.query(Match)
                .filter(
                    Match.tournament_id == match.tournament_id,
                    Match.winner_id.is_(None),
                )
                .count()
            )
            if remaining == 0:
                tournament.status = TournamentStatus.COMPLETED
        elif match.bracket == Bracket.SWISS:
            self._advance_swiss(db, tournament, match.round_number)
        elif match.next_match_id is None:
            # Single-elimination final (no bracket label).
            tournament.status = TournamentStatus.COMPLETED

    def _advance_swiss(
        self, db: Session, tournament: Tournament, round_number: int
    ) -> None:
        """When a swiss round finishes, generate the next one or complete."""
        remaining = (
            db.query(Match)
            .filter(
                Match.tournament_id == tournament.id,
                Match.round_number == round_number,
                Match.bracket == Bracket.SWISS,
                Match.winner_id.is_(None),
            )
            .count()
        )
        if remaining > 0:
            return  # round still in progress

        participants = (
            db.query(Participant)
            .filter(Participant.tournament_id == tournament.id)
            .all()
        )
        if round_number >= total_rounds(len(participants)):
            tournament.status = TournamentStatus.COMPLETED
            return

        self._generate_swiss_round(db, tournament, participants, round_number + 1)

    def _generate_swiss_round(
        self,
        db: Session,
        tournament: Tournament,
        participants: list[Participant],
        round_number: int,
    ) -> None:
        matches = (
            db.query(Match)
            .filter(
                Match.tournament_id == tournament.id,
                Match.bracket == Bracket.SWISS,
            )
            .all()
        )

        wins: dict[int, int] = {p.id: 0 for p in participants}
        played_pairs: set[frozenset] = set()
        byes_had: set[int] = set()
        for m in matches:
            if m.winner_id is not None:
                wins[m.winner_id] = wins.get(m.winner_id, 0) + 1
            if m.player_a_id is not None and m.player_b_id is not None:
                played_pairs.add(frozenset((m.player_a_id, m.player_b_id)))
            elif m.player_a_id is not None and m.player_b_id is None:
                byes_had.add(m.player_a_id)

        seed_of = {
            p.id: (p.seed if p.seed is not None else 10**9) for p in participants
        }
        ordered = sorted(
            (p.id for p in participants),
            key=lambda pid: (-wins.get(pid, 0), seed_of[pid], pid),
        )

        pairings = SwissFormat().next_round_pairings(ordered, played_pairs, byes_had)

        new_matches: list[Match] = []
        for a, b in pairings:
            m = Match(
                tournament_id=tournament.id,
                round_number=round_number,
                player_a_id=a,
                player_b_id=b,
                bracket=Bracket.SWISS,
            )
            db.add(m)
            new_matches.append(m)
        db.flush()

        # Auto-resolve byes (no opponent) so they count as a win immediately.
        for m in new_matches:
            if m.player_b_id is None and m.player_a_id is not None:
                m.winner_id = m.player_a_id
