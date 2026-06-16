import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Bracket } from "../api/types";
import BracketView from "../components/Bracket";
import { useBracketSocket } from "../hooks/useBracketSocket";

// Read-only, login-free view of a tournament, meant to be shared with spectators.
export default function SpectatorPage() {
  const { id } = useParams();
  const tournamentId = Number(id);
  const [bracket, setBracket] = useState<Bracket | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    return api
      .getBracket(tournamentId)
      .then(setBracket)
      .catch((e) => setError(String(e.message ?? e)));
  }, [tournamentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Live updates while spectating.
  useBracketSocket(tournamentId, setBracket);

  if (error && !bracket) return <p className="text-red-400">{error}</p>;
  if (!bracket) return <p className="text-gray-400">Loading…</p>;

  const { tournament } = bracket;

  return (
    <div className="space-y-8">
      <div>
        <Link to="/" className="text-sm text-blue-400 hover:underline">
          ← All tournaments
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{tournament.name}</h1>
        <p className="text-gray-400">{tournament.status} · spectator view</p>
      </div>

      <BracketView
        data={bracket}
        canReport={false}
        onPickWinner={() => {}}
        onCorrectWinner={() => {}}
      />
    </div>
  );
}
