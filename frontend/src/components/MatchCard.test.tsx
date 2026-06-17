import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MatchCard from "./MatchCard";
import type { Match } from "../api/types";

const nameOf = (id: number | null) =>
  id == null ? "" : ({ 1: "Ana", 2: "Bo" } as Record<number, string>)[id] ?? "";

function match(overrides: Partial<Match> = {}): Match {
  return {
    id: 5,
    tournament_id: 1,
    round_number: 1,
    player_a_id: 1,
    player_b_id: 2,
    winner_id: null,
    score_a: null,
    score_b: null,
    next_match_id: 99,
    next_match_slot: "A",
    bracket: null,
    loser_next_match_id: null,
    loser_next_match_slot: null,
    ...overrides,
  };
}

const noop = () => {};

describe("MatchCard", () => {
  it("renders both player names", () => {
    render(
      <MatchCard
        match={match()}
        nameOf={nameOf}
        canReport={false}
        onPickWinner={noop}
        onCorrectWinner={noop}
      />
    );
    expect(screen.getByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Bo")).toBeInTheDocument();
  });

  it("reports the clicked player as winner when allowed", async () => {
    const onPick = vi.fn();
    render(
      <MatchCard
        match={match()}
        nameOf={nameOf}
        canReport
        onPickWinner={onPick}
        onCorrectWinner={noop}
      />
    );
    await userEvent.click(screen.getByRole("button", { name: /Ana/ }));
    expect(onPick).toHaveBeenCalledWith(5, 1, null, null);
  });

  it("does not allow reporting when canReport is false", () => {
    render(
      <MatchCard
        match={match()}
        nameOf={nameOf}
        canReport={false}
        onPickWinner={noop}
        onCorrectWinner={noop}
      />
    );
    expect(screen.getByRole("button", { name: /Ana/ })).toBeDisabled();
  });

  it("shows scores for a decided match", () => {
    render(
      <MatchCard
        match={match({ winner_id: 1, score_a: 2, score_b: 1 })}
        nameOf={nameOf}
        canReport={false}
        onPickWinner={noop}
        onCorrectWinner={noop}
      />
    );
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
  });
});
