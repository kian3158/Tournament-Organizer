export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export type TournamentStatus = "DRAFT" | "ONGOING" | "COMPLETED";

export type TournamentFormat =
  | "SINGLE_ELIM"
  | "DOUBLE_ELIM"
  | "ROUND_ROBIN"
  | "SWISS";

export interface Tournament {
  id: number;
  name: string;
  status: TournamentStatus;
  format: TournamentFormat;
  owner_id: number | null;
  best_of: number;
}

export interface RosterMember {
  id: number;
  name: string;
}

export interface Participant {
  id: number;
  tournament_id: number | null;
  name: string;
  seed: number | null;
  type: string;
  members: RosterMember[];
}

export interface Match {
  id: number;
  tournament_id: number;
  round_number: number;
  player_a_id: number | null;
  player_b_id: number | null;
  winner_id: number | null;
  score_a: number | null;
  score_b: number | null;
  next_match_id: number | null;
  next_match_slot: "A" | "B" | null;
  bracket:
    | "WINNERS"
    | "LOSERS"
    | "GRAND_FINAL"
    | "GRAND_FINAL_RESET"
    | "ROUND_ROBIN"
    | "SWISS"
    | null;
  loser_next_match_id: number | null;
  loser_next_match_slot: "A" | "B" | null;
}

export interface Standing {
  participant_id: number;
  name: string;
  played: number;
  wins: number;
  losses: number;
  points: number;
}

export interface Bracket {
  tournament: Tournament;
  participants: Participant[];
  matches: Match[];
  standings: Standing[] | null;
}
