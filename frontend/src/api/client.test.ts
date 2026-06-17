import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";

afterEach(() => vi.unstubAllGlobals());

function mockFetch(opts: {
  ok?: boolean;
  status?: number;
  statusText?: string;
  jsonValue?: unknown;
}) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: opts.ok ?? true,
      status: opts.status ?? 200,
      statusText: opts.statusText ?? "",
      json: async () => opts.jsonValue,
    })
  );
}

describe("api client", () => {
  it("returns undefined for 204 responses", async () => {
    mockFetch({ status: 204 });
    await expect(api.deleteTournament(1)).resolves.toBeUndefined();
  });

  it("parses JSON for ok responses", async () => {
    mockFetch({ status: 200, jsonValue: [{ id: 1 }] });
    await expect(api.listTournaments()).resolves.toEqual([{ id: 1 }]);
  });

  it("throws the server-provided detail on error", async () => {
    mockFetch({ ok: false, status: 400, jsonValue: { detail: "nope" } });
    await expect(api.createTournament("x")).rejects.toThrow("nope");
  });
});
