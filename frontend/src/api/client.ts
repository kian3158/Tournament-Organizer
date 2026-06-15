import type {
  Bracket,
  Match,
  Participant,
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

  // --- tournaments ---
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
