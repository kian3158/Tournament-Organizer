import { useMemo } from "react";
import type { Match, Standing, Bracket as BracketData } from "../api/types";
import MatchCard from "./MatchCard";

type WinnerHandler = (
  matchId: number,
  winnerId: number,
  scoreA?: number | null,
  scoreB?: number | null
) => void;

interface Props {
  data: BracketData;
  canReport: boolean;
  onPickWinner: WinnerHandler;
  onCorrectWinner: WinnerHandler;
}

type NameOf = (id: number | null) => string;

export default function Bracket({
  data,
  canReport,
  onPickWinner,
  onCorrectWinner,
}: Props) {
  const { tournament, participants, matches } = data;

  const nameOf = useMemo<NameOf>(() => {
    const byId = new Map(participants.map((p) => [p.id, p.name]));
    return (id) => (id == null ? "" : (byId.get(id) ?? `#${id}`));
  }, [participants]);

  if (matches.length === 0) return null;

  const isStandings = matches.some(
    (m) => m.bracket === "ROUND_ROBIN" || m.bracket === "SWISS"
  );
  const isDouble = !isStandings && matches.some((m) => m.bracket);

  const champion =
    tournament.status === "COMPLETED"
      ? data.standings?.length
        ? data.standings[0].participant_id
        : findChampion(matches)
      : null;

  const sectionProps = {
    matches,
    nameOf,
    canReport,
    onPickWinner,
    onCorrectWinner,
  };

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">
        {isStandings ? "Standings & schedule" : "Bracket"}
      </h2>

      {champion != null && (
        <div className="mb-6 rounded-lg border border-win/40 bg-win/10 px-4 py-3 text-win">
          Champion: <span className="font-bold">{nameOf(champion)}</span>
        </div>
      )}

      {isStandings ? (
        <RoundRobin standings={data.standings ?? []} {...sectionProps} />
      ) : isDouble ? (
        <DoubleElimination {...sectionProps} />
      ) : (
        <SingleElimination {...sectionProps} />
      )}
    </section>
  );
}

interface SectionProps {
  matches: Match[];
  nameOf: NameOf;
  canReport: boolean;
  onPickWinner: WinnerHandler;
  onCorrectWinner: WinnerHandler;
}

function SingleElimination({ matches, ...rest }: SectionProps) {
  const rounds = groupByRound(matches);
  const lastRound = rounds[rounds.length - 1].round;
  return (
    <RoundColumns
      rounds={rounds}
      label={(round) => roundLabel(round, lastRound)}
      {...rest}
    />
  );
}

function DoubleElimination({ matches, ...rest }: SectionProps) {
  const winners = matches.filter((m) => m.bracket === "WINNERS");
  const losers = matches.filter((m) => m.bracket === "LOSERS");
  // Hide the reset match until it's actually needed (players assigned).
  const finals = matches.filter(
    (m) =>
      m.bracket === "GRAND_FINAL" ||
      (m.bracket === "GRAND_FINAL_RESET" &&
        (m.player_a_id != null || m.player_b_id != null))
  );

  return (
    <div className="space-y-8">
      <BracketSection title="Winners bracket" matches={winners} {...rest} />
      <BracketSection title="Losers bracket" matches={losers} {...rest} />
      <BracketSection
        title="Grand final"
        matches={finals}
        label={(round, all) =>
          all.length > 1 && round === all[all.length - 1] ? "Reset" : "Final"
        }
        {...rest}
      />
    </div>
  );
}

interface RoundRobinProps extends SectionProps {
  standings: Standing[];
}

function RoundRobin({ standings, matches, ...rest }: RoundRobinProps) {
  const rounds = groupByRound(matches);
  return (
    <div className="space-y-8">
      <StandingsTable standings={standings} />
      <div>
        <h3 className="mb-3 text-lg font-semibold">Schedule</h3>
        <RoundColumns rounds={rounds} {...rest} />
      </div>
    </div>
  );
}

function StandingsTable({ standings }: { standings: Standing[] }) {
  if (standings.length === 0) return null;
  return (
    <div>
      <h3 className="mb-3 text-lg font-semibold">Standings</h3>
      <table className="w-full max-w-lg border-collapse text-sm">
        <thead>
          <tr className="border-b text-left text-muted">
            <th className="py-2 pr-4">#</th>
            <th className="py-2 pr-4">Participant</th>
            <th className="py-2 pr-4 text-center">P</th>
            <th className="py-2 pr-4 text-center">W</th>
            <th className="py-2 pr-4 text-center">L</th>
            <th className="py-2 text-center">Pts</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((s, i) => (
            <tr key={s.participant_id} className="border-b">
              <td className="py-2 pr-4 text-muted">{i + 1}</td>
              <td className="py-2 pr-4 font-medium">{s.name}</td>
              <td className="py-2 pr-4 text-center">{s.played}</td>
              <td className="py-2 pr-4 text-center text-win">{s.wins}</td>
              <td className="py-2 pr-4 text-center text-danger">{s.losses}</td>
              <td className="py-2 text-center font-semibold">{s.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface BracketSectionProps extends SectionProps {
  title: string;
  label?: (round: number, allRounds: number[]) => string;
}

function BracketSection({
  title,
  matches,
  label,
  ...rest
}: BracketSectionProps) {
  if (matches.length === 0) return null;
  const rounds = groupByRound(matches);
  return (
    <div>
      <h3 className="mb-3 text-lg font-semibold">{title}</h3>
      <RoundColumns rounds={rounds} label={label} {...rest} />
    </div>
  );
}

interface RoundColumnsProps {
  rounds: { round: number; matches: Match[] }[];
  label?: (round: number, allRounds: number[]) => string;
  nameOf: NameOf;
  canReport: boolean;
  onPickWinner: WinnerHandler;
  onCorrectWinner: WinnerHandler;
}

function RoundColumns({
  rounds,
  label,
  nameOf,
  canReport,
  onPickWinner,
  onCorrectWinner,
}: RoundColumnsProps) {
  const roundNumbers = rounds.map((r) => r.round);
  return (
    <div className="flex gap-10 overflow-x-auto pb-4">
      {rounds.map(({ round, matches }) => (
        <div key={round} className="flex flex-col justify-around gap-4">
          <h4 className="text-center text-sm font-semibold uppercase tracking-wide text-muted">
            {label ? label(round, roundNumbers) : `Round ${round}`}
          </h4>
          {matches.map((m) => (
            <MatchCard
              key={m.id}
              match={m}
              nameOf={nameOf}
              canReport={canReport}
              onPickWinner={onPickWinner}
              onCorrectWinner={onCorrectWinner}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

function groupByRound(matches: Match[]): { round: number; matches: Match[] }[] {
  const byRound = new Map<number, Match[]>();
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
}

function findChampion(matches: Match[]): number | null {
  const reset = matches.find((m) => m.bracket === "GRAND_FINAL_RESET");
  if (reset?.winner_id != null) return reset.winner_id;
  const grandFinal = matches.find((m) => m.bracket === "GRAND_FINAL");
  if (grandFinal?.winner_id != null) return grandFinal.winner_id;
  // Single elimination: the final is the match with no next.
  const final = matches.find(
    (m) => m.bracket == null && m.next_match_id == null
  );
  return final?.winner_id ?? null;
}

function roundLabel(round: number, lastRound: number): string {
  const fromEnd = lastRound - round;
  if (fromEnd === 0) return "Final";
  if (fromEnd === 1) return "Semifinals";
  if (fromEnd === 2) return "Quarterfinals";
  return `Round ${round}`;
}
