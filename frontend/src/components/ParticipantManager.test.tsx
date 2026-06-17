import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ParticipantManager from "./ParticipantManager";
import type { Participant } from "../api/types";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: {
    addParticipant: vi.fn().mockResolvedValue({}),
    deleteParticipant: vi.fn().mockResolvedValue(undefined),
    updateParticipant: vi.fn().mockResolvedValue({}),
    reorderParticipants: vi.fn().mockResolvedValue([]),
  },
}));

function participant(overrides: Partial<Participant> = {}): Participant {
  return {
    id: 1,
    tournament_id: 1,
    name: "Ana",
    seed: 1,
    type: "PLAYER",
    members: [],
    ...overrides,
  };
}

beforeEach(() => vi.clearAllMocks());

describe("ParticipantManager", () => {
  it("lists participants", () => {
    render(
      <ParticipantManager
        tournamentId={1}
        participants={[participant(), participant({ id: 2, name: "Bo", seed: 2 })]}
        editable={false}
        onChange={() => {}}
      />
    );
    expect(screen.getByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Bo")).toBeInTheDocument();
  });

  it("hides the add form when not editable", () => {
    render(
      <ParticipantManager
        tournamentId={1}
        participants={[participant()]}
        editable={false}
        onChange={() => {}}
      />
    );
    expect(
      screen.queryByPlaceholderText("Participant name")
    ).not.toBeInTheDocument();
  });

  it("adds a participant through the form", async () => {
    const onChange = vi.fn();
    render(
      <ParticipantManager
        tournamentId={7}
        participants={[]}
        editable
        onChange={onChange}
      />
    );
    await userEvent.type(
      screen.getByPlaceholderText("Participant name"),
      "Cy"
    );
    await userEvent.click(screen.getByRole("button", { name: "Add" }));
    expect(api.addParticipant).toHaveBeenCalledWith(7, "Cy", null, "PLAYER");
  });
});
