import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Bracket } from "../api/types";
import BracketView from "../components/Bracket";
import ParticipantManager from "../components/ParticipantManager";

export default function TournamentPage() {
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

  async function handleGenerate() {
    setError(null);
    try {
      await api.generateBracket(tournamentId);
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  async function handlePickWinner(matchId: number, winnerId: number) {
    setError(null);
    try {
      await api.reportResult(matchId, winnerId);
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  if (error && !bracket) return <p className="text-red-400">{error}</p>;
  if (!bracket) return <p className="text-gray-400">Loading…</p>;

  const { tournament, participants } = bracket;
  const isDraft = tournament.status === "DRAFT";
  const canGenerate = isDraft && participants.length >= 2;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <Link to="/" className="text-sm text-blue-400 hover:underline">
            ← All tournaments
          </Link>
          <h1 className="mt-2 text-2xl font-bold">{tournament.name}</h1>
          <p className="text-gray-400">{tournament.status}</p>
        </div>
        {isDraft && (
          <button
            onClick={handleGenerate}
            disabled={!canGenerate}
            title={canGenerate ? "" : "Add at least 2 participants first"}
            className="rounded-md bg-green-600 px-5 py-2 font-medium hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Generate bracket
          </button>
        )}
      </div>

      {error && <p className="text-red-400">{error}</p>}

      <ParticipantManager
        tournamentId={tournamentId}
        participants={participants}
        editable={isDraft}
        onChange={refresh}
      />

      <BracketView data={bracket} onPickWinner={handlePickWinner} />
    </div>
  );
}
