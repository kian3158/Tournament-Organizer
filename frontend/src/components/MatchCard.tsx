import { useState } from "react";
import type { Match } from "../api/types";
import { CheckIcon } from "./icons";

interface Props {
  match: Match;
  nameOf: (id: number | null) => string;
  canReport: boolean;
  onPickWinner: (
    matchId: number,
    winnerId: number,
    scoreA?: number | null,
    scoreB?: number | null
  ) => void;
  onCorrectWinner: (matchId: number, winnerId: number) => void;
}

export default function MatchCard({
  match,
  nameOf,
  canReport,
  onPickWinner,
  onCorrectWinner,
}: Props) {
  const [scoreA, setScoreA] = useState("");
  const [scoreB, setScoreB] = useState("");

  const bothPlayers = match.player_a_id != null && match.player_b_id != null;
  const ready = bothPlayers && match.winner_id == null;
  const decided = bothPlayers && match.winner_id != null;
  const showScoreInputs = canReport && ready;

  // Click an empty (no-winner) match to report; click the loser of a decided
  // match to switch the result.
  function slotFor(playerId: number | null, score: number | null) {
    const isWinner = match.winner_id != null && match.winner_id === playerId;
    const canPick = canReport && ready && playerId != null;
    const canFix = canReport && decided && playerId != null && !isWinner;
    return {
      label: slotLabel(match, playerId),
      playerId,
      isWinner,
      score: decided ? score : null,
      clickable: canPick || canFix,
      title: canFix ? "Change the winner to this player" : undefined,
      onClick: () => {
        if (playerId == null) return;
        if (canPick) {
          const a = scoreA.trim() ? Number(scoreA) : null;
          const b = scoreB.trim() ? Number(scoreB) : null;
          onPickWinner(match.id, playerId, a, b);
        } else if (canFix) {
          onCorrectWinner(match.id, playerId);
        }
      },
    };
  }

  return (
    <div className="w-52 overflow-hidden rounded-lg border bg-surface text-sm shadow-sm">
      <Slot nameOf={nameOf} {...slotFor(match.player_a_id, match.score_a)} />
      <div className="border-t" />
      <Slot nameOf={nameOf} {...slotFor(match.player_b_id, match.score_b)} />
      {showScoreInputs && (
        <div className="flex items-center gap-2 border-t bg-elevated px-3 py-2">
          <ScoreInput value={scoreA} onChange={setScoreA} />
          <span className="text-muted">:</span>
          <ScoreInput value={scoreB} onChange={setScoreB} />
          <span className="ml-auto text-xs text-muted">score (optional)</span>
        </div>
      )}
    </div>
  );
}

function ScoreInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <input
      type="number"
      min="0"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-10 rounded border bg-surface px-1 py-0.5 text-center outline-none focus:border-accent"
    />
  );
}

function slotLabel(match: Match, playerId: number | null): string | null {
  if (playerId != null) return null;
  // In swiss, an empty slot is always a bye (no opponent this round).
  if (match.bracket === "SWISS") return "BYE";
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
  score: number | null;
  clickable: boolean;
  nameOf: (id: number | null) => string;
  onClick: () => void;
  title?: string;
}

function Slot({
  playerId,
  label,
  isWinner,
  score,
  clickable,
  nameOf,
  onClick,
  title,
}: SlotProps) {
  const text = playerId != null ? nameOf(playerId) : label;
  const base = "flex items-center justify-between gap-2 px-3 py-2";
  const state = isWinner
    ? "bg-win/15 font-semibold text-win"
    : playerId == null
      ? "italic text-muted"
      : "";
  const hover = clickable ? "cursor-pointer hover:bg-accent/10" : "";

  return (
    <button
      type="button"
      disabled={!clickable}
      onClick={onClick}
      title={title}
      className={`w-full text-left ${base} ${state} ${hover} disabled:cursor-default`}
    >
      <span className="truncate">{text}</span>
      <span className="flex shrink-0 items-center gap-1.5">
        {score != null && <span className="tabular-nums">{score}</span>}
        {isWinner && <CheckIcon className="text-win" size={16} />}
      </span>
    </button>
  );
}
