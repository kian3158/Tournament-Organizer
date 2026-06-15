import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Tournament } from "../api/types";

export default function TournamentPage() {
  const { id } = useParams();
  const tournamentId = Number(id);
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getTournament(tournamentId)
      .then(setTournament)
      .catch((e) => setError(String(e.message ?? e)));
  }, [tournamentId]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!tournament) return <p className="text-gray-400">Loading…</p>;

  return (
    <div className="space-y-8">
      <div>
        <Link to="/" className="text-sm text-blue-400 hover:underline">
          ← All tournaments
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{tournament.name}</h1>
        <p className="text-gray-400">{tournament.status}</p>
      </div>
    </div>
  );
}
