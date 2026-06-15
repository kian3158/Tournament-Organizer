import type {
  Bracket,
  Match,
  Participant,
  Tournament,
  TournamentFormat,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response had no JSON body; keep the status text
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listTournaments: () => request<Tournament[]>("/tournaments"),

  getTournament: (id: number) => request<Tournament>(`/tournaments/${id}`),

  createTournament: (name: string, format: TournamentFormat = "SINGLE_ELIM") =>
    request<Tournament>("/tournaments", {
      method: "POST",
      body: JSON.stringify({ name, format }),
    }),

  listParticipants: (tournamentId: number) =>
    request<Participant[]>(`/tournaments/${tournamentId}/participants`),

  addParticipant: (tournamentId: number, name: string, seed?: number | null) =>
    request<Participant>(`/tournaments/${tournamentId}/participants`, {
      method: "POST",
      body: JSON.stringify({ name, seed: seed ?? null }),
    }),

  generateBracket: (tournamentId: number) =>
    request<Bracket>(`/tournaments/${tournamentId}/generate`, {
      method: "POST",
    }),

  getBracket: (tournamentId: number) =>
    request<Bracket>(`/tournaments/${tournamentId}/bracket`),

  reportResult: (matchId: number, winnerId: number) =>
    request<Match>(`/matches/${matchId}/result`, {
      method: "POST",
      body: JSON.stringify({ winner_id: winnerId }),
    }),
};
