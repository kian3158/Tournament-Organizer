import { useState } from "react";
import { api } from "../api/client";
import type { Participant } from "../api/types";

interface Props {
  tournamentId: number;
  participants: Participant[];
  editable: boolean;
  onChange: () => void;
}

export default function ParticipantManager({
  tournamentId,
  participants,
  editable,
  onChange,
}: Props) {
  const [name, setName] = useState("");
  const [seed, setSeed] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    try {
      await api.addParticipant(
        tournamentId,
        name.trim(),
        seed.trim() ? Number(seed) : null
      );
      setName("");
      setSeed("");
      onChange();
    } catch (e) {
      setError(String((e as Error).message));
    }
  }

  const sorted = [...participants].sort(
    (a, b) => (a.seed ?? Infinity) - (b.seed ?? Infinity) || a.id - b.id
  );

  return (
    <section>
      <h2 className="mb-3 text-xl font-semibold">
        Participants{" "}
        <span className="text-gray-500">({participants.length})</span>
      </h2>

      {editable && (
        <form onSubmit={handleAdd} className="mb-4 flex gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Participant name"
            className="flex-1 rounded-md border border-gray-700 bg-gray-800 px-4 py-2 outline-none focus:border-blue-500"
          />
          <input
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="Seed (optional)"
            type="number"
            min="1"
            className="w-36 rounded-md border border-gray-700 bg-gray-800 px-4 py-2 outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="rounded-md bg-blue-600 px-5 py-2 font-medium hover:bg-blue-500"
          >
            Add
          </button>
        </form>
      )}
      {error && <p className="mb-3 text-red-400">{error}</p>}

      {participants.length === 0 ? (
        <p className="text-gray-400">No participants yet.</p>
      ) : (
        <ul className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {sorted.map((p) => (
            <li
              key={p.id}
              className="flex items-center gap-2 rounded-md border border-gray-800 bg-gray-900 px-3 py-2"
            >
              {p.seed != null && (
                <span className="text-xs font-semibold text-gray-500">
                  #{p.seed}
                </span>
              )}
              <span>{p.name}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
