import type {
  Bracket,
  Match,
  Participant,
  ParticipantStat,
  RosterMember,
  Token,
  Tournament,
  TournamentFormat,
  User,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const TOKEN_KEY = "token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function bracketSocketUrl(tournamentId: number): string {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  return `${wsBase}/ws/tournaments/${tournamentId}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
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
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  // --- auth ---
  register: (email: string, password: string) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<Token>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/auth/me"),

  getMyStats: () => request<ParticipantStat[]>("/stats"),

  // --- tournaments ---
  listTournaments: () => request<Tournament[]>("/tournaments"),

  getTournament: (id: number) => request<Tournament>(`/tournaments/${id}`),

  createTournament: (
    name: string,
    format: TournamentFormat = "SINGLE_ELIM",
    bestOf = 1,
    thirdPlace = false
  ) =>
    request<Tournament>("/tournaments", {
      method: "POST",
      body: JSON.stringify({
        name,
        format,
        best_of: bestOf,
        third_place: thirdPlace,
      }),
    }),

  listParticipants: (tournamentId: number) =>
    request<Participant[]>(`/tournaments/${tournamentId}/participants`),

  addParticipant: (
    tournamentId: number,
    name: string,
    seed?: number | null,
    type: string = "PLAYER"
  ) =>
    request<Participant>(`/tournaments/${tournamentId}/participants`, {
      method: "POST",
      body: JSON.stringify({ name, seed: seed ?? null, type }),
    }),

  addMember: (tournamentId: number, participantId: number, name: string) =>
    request<RosterMember>(
      `/tournaments/${tournamentId}/participants/${participantId}/members`,
      { method: "POST", body: JSON.stringify({ name }) }
    ),

  updateMember: (
    tournamentId: number,
    participantId: number,
    memberId: number,
    name: string
  ) =>
    request<RosterMember>(
      `/tournaments/${tournamentId}/participants/${participantId}/members/${memberId}`,
      { method: "PATCH", body: JSON.stringify({ name }) }
    ),

  deleteMember: (
    tournamentId: number,
    participantId: number,
    memberId: number
  ) =>
    request<void>(
      `/tournaments/${tournamentId}/participants/${participantId}/members/${memberId}`,
      { method: "DELETE" }
    ),

  updateParticipant: (
    tournamentId: number,
    participantId: number,
    fields: { name?: string; seed?: number | null }
  ) =>
    request<Participant>(
      `/tournaments/${tournamentId}/participants/${participantId}`,
      { method: "PATCH", body: JSON.stringify(fields) }
    ),

  deleteParticipant: (tournamentId: number, participantId: number) =>
    request<void>(
      `/tournaments/${tournamentId}/participants/${participantId}`,
      { method: "DELETE" }
    ),

  reorderParticipants: (tournamentId: number, participantIds: number[]) =>
    request<Participant[]>(`/tournaments/${tournamentId}/participants/order`, {
      method: "PUT",
      body: JSON.stringify({ participant_ids: participantIds }),
    }),

  deleteTournament: (tournamentId: number) =>
    request<void>(`/tournaments/${tournamentId}`, { method: "DELETE" }),

  generateBracket: (tournamentId: number) =>
    request<Bracket>(`/tournaments/${tournamentId}/generate`, {
      method: "POST",
    }),

  getBracket: (tournamentId: number) =>
    request<Bracket>(`/tournaments/${tournamentId}/bracket`),

  reportResult: (
    matchId: number,
    winnerId: number,
    scoreA?: number | null,
    scoreB?: number | null
  ) =>
    request<Match>(`/matches/${matchId}/result`, {
      method: "POST",
      body: JSON.stringify({
        winner_id: winnerId,
        score_a: scoreA ?? null,
        score_b: scoreB ?? null,
      }),
    }),

  correctResult: (matchId: number, winnerId: number) =>
    request<Match>(`/matches/${matchId}/result`, {
      method: "PATCH",
      body: JSON.stringify({ winner_id: winnerId }),
    }),
};
