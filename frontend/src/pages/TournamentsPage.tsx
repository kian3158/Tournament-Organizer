import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Tournament, TournamentFormat } from "../api/types";

export default function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [name, setName] = useState("");
  const [format, setFormat] = useState<TournamentFormat>("SINGLE_ELIM");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setTournaments(await api.listTournaments());
    setLoading(false);
  }

  useEffect(() => {
    refresh().catch((e) => {
      setError(String(e.message ?? e));
      setLoading(false);
    });
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    try {
      await api.createTournament(name.trim(), format);
      setName("");
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  return (
    <div className="space-y-10">
      <section className="rounded-xl border bg-surface p-5 shadow-sm">
        <h1 className="mb-4 text-xl font-semibold">New tournament</h1>
        <form onSubmit={handleCreate} className="flex flex-wrap gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Tournament name"
            className="flex-1 rounded-lg border bg-bg px-4 py-2 outline-none transition-colors placeholder:text-muted focus:border-accent"
          />
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value as TournamentFormat)}
            className="rounded-lg border bg-bg px-3 py-2 outline-none transition-colors focus:border-accent"
          >
            <option value="SINGLE_ELIM">Single elimination</option>
            <option value="DOUBLE_ELIM">Double elimination</option>
            <option value="ROUND_ROBIN">Round robin</option>
            <option value="SWISS">Swiss</option>
          </select>
          <button
            type="submit"
            className="rounded-lg bg-accent px-5 py-2 font-medium text-accent-fg transition-colors hover:bg-accent-hover"
          >
            Create
          </button>
        </form>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Tournaments</h2>
        {error && <p className="text-danger">{error}</p>}
        {loading ? (
          <p className="text-muted">Loading…</p>
        ) : tournaments.length === 0 ? (
          <p className="text-muted">No tournaments yet. Create one above.</p>
        ) : (
          <ul className="divide-y overflow-hidden rounded-xl border bg-surface">
            {tournaments.map((t) => (
              <li key={t.id}>
                <Link
                  to={`/tournaments/${t.id}`}
                  className="flex items-center justify-between px-4 py-3.5 transition-colors hover:bg-elevated"
                >
                  <span className="font-medium">{t.name}</span>
                  <StatusBadge status={t.status} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function StatusBadge({ status }: { status: Tournament["status"] }) {
  const styles: Record<Tournament["status"], string> = {
    DRAFT: "bg-elevated text-muted",
    ONGOING: "bg-accent/15 text-accent",
    COMPLETED: "bg-win/15 text-win",
  };
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${styles[status]}`}
    >
      {status}
    </span>
  );
}
