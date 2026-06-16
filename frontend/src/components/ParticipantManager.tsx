import { useState } from "react";
import { api } from "../api/client";
import type { Participant } from "../api/types";
import { CheckIcon, CloseIcon, PencilIcon, TrashIcon } from "./icons";

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
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");

  function fail(e: unknown) {
    setError(String((e as Error).message));
  }

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
      fail(e);
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await api.deleteParticipant(tournamentId, id);
      onChange();
    } catch (e) {
      fail(e);
    }
  }

  async function handleSaveEdit(id: number) {
    if (!editName.trim()) return;
    setError(null);
    try {
      await api.updateParticipant(tournamentId, id, { name: editName.trim() });
      setEditingId(null);
      onChange();
    } catch (e) {
      fail(e);
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
              {editingId === p.id ? (
                <>
                  <input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSaveEdit(p.id)}
                    autoFocus
                    className="min-w-0 flex-1 rounded border border-gray-700 bg-gray-800 px-2 py-1"
                  />
                  <button
                    onClick={() => handleSaveEdit(p.id)}
                    className="text-green-400 hover:text-green-300"
                    title="Save"
                  >
                    <CheckIcon />
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="text-gray-500 hover:text-gray-300"
                    title="Cancel"
                  >
                    <CloseIcon />
                  </button>
                </>
              ) : (
                <>
                  {p.seed != null && (
                    <span className="text-xs font-semibold text-gray-500">
                      #{p.seed}
                    </span>
                  )}
                  <span className="flex-1 truncate">{p.name}</span>
                  {editable && (
                    <>
                      <button
                        onClick={() => {
                          setEditingId(p.id);
                          setEditName(p.name);
                        }}
                        className="text-gray-500 hover:text-blue-400"
                        title="Rename"
                      >
                        <PencilIcon />
                      </button>
                      <button
                        onClick={() => handleDelete(p.id)}
                        className="text-gray-500 hover:text-red-400"
                        title="Remove"
                      >
                        <TrashIcon />
                      </button>
                    </>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
