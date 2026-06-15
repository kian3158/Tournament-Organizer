import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Tournament } from "../api/types";

export default function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [name, setName] = useState("");
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
      await api.createTournament(name.trim());
      setName("");
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  return (
    <div className="space-y-8">
      <section>
        <h1 className="mb-4 text-2xl font-bold">New tournament</h1>
        <form onSubmit={handleCreate} className="flex gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Tournament name"
            className="flex-1 rounded-md border border-gray-700 bg-gray-800 px-4 py-2 outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="rounded-md bg-blue-600 px-5 py-2 font-medium hover:bg-blue-500"
          >
            Create
          </button>
        </form>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Tournaments</h2>
        {error && <p className="text-red-400">{error}</p>}
        {loading ? (
          <p className="text-gray-400">Loading…</p>
        ) : tournaments.length === 0 ? (
          <p className="text-gray-400">No tournaments yet. Create one above.</p>
        ) : (
          <ul className="divide-y divide-gray-800 rounded-md border border-gray-800">
            {tournaments.map((t) => (
              <li key={t.id}>
                <Link
                  to={`/tournaments/${t.id}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-gray-800"
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
    DRAFT: "bg-gray-700 text-gray-200",
    ONGOING: "bg-blue-900 text-blue-200",
    COMPLETED: "bg-green-900 text-green-200",
  };
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
}
