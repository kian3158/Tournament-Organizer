import type { Match } from "../api/types";

interface Props {
  match: Match;
  nameOf: (id: number | null) => string;
  canReport: boolean;
  onPickWinner: (matchId: number, winnerId: number) => void;
}

export default function MatchCard({
  match,
  nameOf,
  canReport,
  onPickWinner,
}: Props) {
  const ready =
    match.player_a_id != null &&
    match.player_b_id != null &&
    match.winner_id == null;
  const clickable = canReport && ready;

  return (
    <div className="w-52 overflow-hidden rounded-md border border-gray-700 bg-gray-900 text-sm">
      <Slot
        label={slotLabel(match, match.player_a_id)}
        playerId={match.player_a_id}
        isWinner={match.winner_id != null && match.winner_id === match.player_a_id}
        nameOf={nameOf}
        clickable={clickable && match.player_a_id != null}
        onClick={() => match.player_a_id && onPickWinner(match.id, match.player_a_id)}
      />
      <div className="border-t border-gray-700" />
      <Slot
        label={slotLabel(match, match.player_b_id)}
        playerId={match.player_b_id}
        isWinner={match.winner_id != null && match.winner_id === match.player_b_id}
        nameOf={nameOf}
        clickable={clickable && match.player_b_id != null}
        onClick={() => match.player_b_id && onPickWinner(match.id, match.player_b_id)}
      />
    </div>
  );
}

function slotLabel(match: Match, playerId: number | null): string | null {
  if (playerId != null) return null;
  // Empty first-round slots are byes only in elimination round 1; everywhere
  // else (later rounds, losers bracket, grand final) the slot is pending.
  const isElimFirstRound =
    match.round_number === 1 &&
    (match.bracket == null || match.bracket === "WINNERS");
  return isElimFirstRound ? "BYE" : "TBD";
}

interface SlotProps {
  playerId: number | null;
  label: string | null;
  isWinner: boolean;
  clickable: boolean;
  nameOf: (id: number | null) => string;
  onClick: () => void;
}

function Slot({ playerId, label, isWinner, clickable, nameOf, onClick }: SlotProps) {
  const text = playerId != null ? nameOf(playerId) : label;
  const base = "flex items-center justify-between px-3 py-2";
  const state = isWinner
    ? "bg-green-900/60 font-semibold text-green-200"
    : playerId == null
      ? "text-gray-500 italic"
      : "";
  const hover = clickable ? "cursor-pointer hover:bg-blue-900/50" : "";

  return (
    <button
      type="button"
      disabled={!clickable}
      onClick={onClick}
      className={`w-full text-left ${base} ${state} ${hover} disabled:cursor-default`}
    >
      <span className="truncate">{text}</span>
      {isWinner && <span className="text-green-300">✓</span>}
    </button>
  );
}
