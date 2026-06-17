import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Tournament, TournamentFormat } from "../api/types";

interface Preset {
  label: string;
  format: TournamentFormat;
  bestOf: number;
  thirdPlace: boolean;
}

// Quick starting points for common game-night setups.
const PRESETS: Preset[] = [
  { label: "Game night", format: "SINGLE_ELIM", bestOf: 1, thirdPlace: true },
  { label: "Bo3 cup", format: "SINGLE_ELIM", bestOf: 3, thirdPlace: true },
  { label: "Double elim", format: "DOUBLE_ELIM", bestOf: 3, thirdPlace: false },
  { label: "Round robin", format: "ROUND_ROBIN", bestOf: 1, thirdPlace: false },
  { label: "Swiss", format: "SWISS", bestOf: 3, thirdPlace: false },
];

export default function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [name, setName] = useState("");
  const [format, setFormat] = useState<TournamentFormat>("SINGLE_ELIM");
  const [bestOf, setBestOf] = useState(1);
  const [thirdPlace, setThirdPlace] = useState(false);
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

  function applyPreset(p: Preset) {
    setFormat(p.format);
    setBestOf(p.bestOf);
    setThirdPlace(p.thirdPlace);
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    try {
      await api.createTournament(name.trim(), format, bestOf, thirdPlace);
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
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted">Presets:</span>
          {PRESETS.map((p) => (
            <button
              key={p.label}
              type="button"
              onClick={() => applyPreset(p)}
              className="rounded-full border px-3 py-1 text-sm transition-colors hover:bg-elevated"
            >
              {p.label}
            </button>
          ))}
        </div>
        <form
          onSubmit={handleCreate}
          className="flex flex-wrap items-center gap-3"
        >
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
          <select
            value={bestOf}
            onChange={(e) => setBestOf(Number(e.target.value))}
            title="Games needed to win a match"
            className="rounded-lg border bg-bg px-3 py-2 outline-none transition-colors focus:border-accent"
          >
            <option value={1}>Single game</option>
            <option value={3}>Best of 3</option>
            <option value={5}>Best of 5</option>
            <option value={7}>Best of 7</option>
          </select>
          {format === "SINGLE_ELIM" && (
            <label className="flex items-center gap-2 text-sm text-muted">
              <input
                type="checkbox"
                checked={thirdPlace}
                onChange={(e) => setThirdPlace(e.target.checked)}
                className="accent-accent"
              />
              3rd place
            </label>
          )}
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
