import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ParticipantStat } from "../api/types";

export default function StatsPage() {
  const [stats, setStats] = useState<ParticipantStat[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getMyStats()
      .then(setStats)
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  if (error) return <p className="text-danger">{error}</p>;
  if (!stats) return <p className="text-muted">Loading…</p>;

  return (
    <section>
      <h1 className="mb-1 text-2xl font-semibold">Stats</h1>
      <p className="mb-5 text-sm text-muted">
        Results by participant name across all your tournaments.
      </p>

      {stats.length === 0 ? (
        <p className="text-muted">
          No results yet — play some matches and they'll show up here.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-xl border bg-surface">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b text-left text-muted">
                <th className="px-4 py-3">Participant</th>
                <th className="px-4 py-3 text-center">Tournaments</th>
                <th className="px-4 py-3 text-center">Played</th>
                <th className="px-4 py-3 text-center">W</th>
                <th className="px-4 py-3 text-center">L</th>
                <th className="px-4 py-3 text-center">Titles</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((s) => (
                <tr key={s.name} className="border-b last:border-0">
                  <td className="px-4 py-3 font-medium">{s.name}</td>
                  <td className="px-4 py-3 text-center">{s.tournaments}</td>
                  <td className="px-4 py-3 text-center">{s.played}</td>
                  <td className="px-4 py-3 text-center text-win">{s.wins}</td>
                  <td className="px-4 py-3 text-center text-danger">{s.losses}</td>
                  <td className="px-4 py-3 text-center font-semibold">
                    {s.titles}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
