import { useMemo } from "react";
import type { Bracket as BracketData } from "../api/types";
import MatchCard from "./MatchCard";

interface Props {
  data: BracketData;
  canReport: boolean;
  onPickWinner: (matchId: number, winnerId: number) => void;
}

export default function Bracket({ data, canReport, onPickWinner }: Props) {
  const { tournament, participants, matches } = data;

  const nameOf = useMemo(() => {
    const byId = new Map(participants.map((p) => [p.id, p.name]));
    return (id: number | null) =>
      id == null ? "" : (byId.get(id) ?? `#${id}`);
  }, [participants]);

  const rounds = useMemo(() => {
    const byRound = new Map<number, typeof matches>();
    for (const m of matches) {
      const list = byRound.get(m.round_number) ?? [];
      list.push(m);
      byRound.set(m.round_number, list);
    }
    return [...byRound.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([round, ms]) => ({
        round,
        matches: ms.sort((a, b) => a.id - b.id),
      }));
  }, [matches]);

  if (matches.length === 0) return null;

  const lastRound = rounds[rounds.length - 1].round;

  const champion =
    tournament.status === "COMPLETED"
      ? (rounds.at(-1)?.matches[0]?.winner_id ?? null)
      : null;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Bracket</h2>

      {champion != null && (
        <div className="mb-6 rounded-md border border-green-700 bg-green-900/40 px-4 py-3 text-green-200">
          🏆 Champion: <span className="font-bold">{nameOf(champion)}</span>
        </div>
      )}

      <div className="flex gap-10 overflow-x-auto pb-4">
        {rounds.map(({ round, matches }) => (
          <div key={round} className="flex flex-col justify-around gap-4">
            <h3 className="text-center text-sm font-semibold uppercase tracking-wide text-gray-400">
              {roundLabel(round, lastRound)}
            </h3>
            {matches.map((m) => (
              <MatchCard
                key={m.id}
                match={m}
                nameOf={nameOf}
                canReport={canReport}
                onPickWinner={onPickWinner}
              />
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

function roundLabel(round: number, lastRound: number): string {
  const fromEnd = lastRound - round;
  if (fromEnd === 0) return "Final";
  if (fromEnd === 1) return "Semifinals";
  if (fromEnd === 2) return "Quarterfinals";
  return `Round ${round}`;
}
