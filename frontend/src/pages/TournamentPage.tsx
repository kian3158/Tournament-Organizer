import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { Bracket } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import BracketView from "../components/Bracket";
import ParticipantManager from "../components/ParticipantManager";
import { useBracketSocket } from "../hooks/useBracketSocket";

export default function TournamentPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const tournamentId = Number(id);
  const [bracket, setBracket] = useState<Bracket | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const refresh = useCallback(() => {
    return api
      .getBracket(tournamentId)
      .then(setBracket)
      .catch((e) => setError(String(e.message ?? e)));
  }, [tournamentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Live updates: the server pushes a fresh bracket whenever it changes.
  // The socket needs the share token, which arrives with the bracket data.
  useBracketSocket(tournamentId, setBracket, bracket?.tournament.share_token);

  async function handleGenerate() {
    setError(null);
    try {
      await api.generateBracket(tournamentId);
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  async function handlePickWinner(
    matchId: number,
    winnerId: number,
    scoreA?: number | null,
    scoreB?: number | null
  ) {
    setError(null);
    try {
      await api.reportResult(matchId, winnerId, scoreA, scoreB);
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  async function handleCorrectWinner(matchId: number, winnerId: number) {
    setError(null);
    try {
      await api.correctResult(matchId, winnerId);
      await refresh();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  async function handleCopyLink() {
    const token = bracket?.tournament.share_token ?? "";
    const url = `${window.location.origin}/watch/${tournamentId}?token=${token}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      window.prompt("Copy this spectator link:", url);
    }
  }

  async function handleDeleteTournament() {
    if (!window.confirm("Delete this tournament? This can't be undone.")) return;
    setError(null);
    try {
      await api.deleteTournament(tournamentId);
      navigate("/");
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  if (error && !bracket) return <p className="text-danger">{error}</p>;
  if (!bracket) return <p className="text-muted">Loading…</p>;

  const { tournament, participants } = bracket;
  const isOwner = user != null && tournament.owner_id === user.id;
  const isDraft = tournament.status === "DRAFT";
  const canGenerate = isOwner && isDraft && participants.length >= 2;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to="/" className="text-sm text-accent hover:underline">
            ← All tournaments
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">{tournament.name}</h1>
          <p className="text-sm text-muted">
            {tournament.status}
            {tournament.best_of > 1 && ` · Best of ${tournament.best_of}`}
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopyLink}
            className="rounded-lg border px-4 py-2 text-sm font-medium transition-colors hover:bg-elevated"
          >
            {copied ? "Copied!" : "Share"}
          </button>
          {isOwner && isDraft && (
            <button
              onClick={handleGenerate}
              disabled={!canGenerate}
              title={canGenerate ? "" : "Add at least 2 participants first"}
              className="rounded-lg bg-accent px-5 py-2 font-medium text-accent-fg transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-40"
            >
              Generate bracket
            </button>
          )}
          {isOwner && (
            <button
              onClick={handleDeleteTournament}
              className="rounded-lg border border-danger/40 px-4 py-2 text-sm font-medium text-danger transition-colors hover:bg-danger/10"
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {error && <p className="text-danger">{error}</p>}

      <ParticipantManager
        tournamentId={tournamentId}
        participants={participants}
        editable={isOwner && isDraft}
        onChange={refresh}
      />

      <BracketView
        data={bracket}
        canReport={isOwner && tournament.status === "ONGOING"}
        onPickWinner={handlePickWinner}
        onCorrectWinner={handleCorrectWinner}
      />
    </div>
  );
}
