import { useState } from "react";
import { api } from "../api/client";
import type { Participant } from "../api/types";
import { CheckIcon, CloseIcon, PencilIcon, TrashIcon } from "./icons";

interface Props {
  tournamentId: number;
  participant: Participant;
  editable: boolean;
  onChange: () => void;
}

export default function RosterEditor({
  tournamentId,
  participant,
  editable,
  onChange,
}: Props) {
  const [name, setName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fail = (e: unknown) => setError(String((e as Error).message));

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    try {
      await api.addMember(tournamentId, participant.id, name.trim());
      setName("");
      onChange();
    } catch (e) {
      fail(e);
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await api.deleteMember(tournamentId, participant.id, id);
      onChange();
    } catch (e) {
      fail(e);
    }
  }

  async function handleSave(id: number) {
    if (!editName.trim()) return;
    setError(null);
    try {
      await api.updateMember(tournamentId, participant.id, id, editName.trim());
      setEditingId(null);
      onChange();
    } catch (e) {
      fail(e);
    }
  }

  const members = participant.members;

  return (
    <div className="mt-2 border-t border-gray-800 pt-2">
      {members.length === 0 && (
        <p className="text-xs text-gray-500">No members yet.</p>
      )}
      <ul className="space-y-1">
        {members.map((m) => (
          <li key={m.id} className="flex items-center gap-2 text-sm">
            {editingId === m.id ? (
              <>
                <input
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSave(m.id)}
                  autoFocus
                  className="min-w-0 flex-1 rounded border border-gray-700 bg-gray-800 px-2 py-0.5"
                />
                <button
                  onClick={() => handleSave(m.id)}
                  className="text-green-400 hover:text-green-300"
                  title="Save"
                >
                  <CheckIcon size={13} />
                </button>
                <button
                  onClick={() => setEditingId(null)}
                  className="text-gray-500 hover:text-gray-300"
                  title="Cancel"
                >
                  <CloseIcon size={13} />
                </button>
              </>
            ) : (
              <>
                <span className="flex-1 truncate text-gray-300">{m.name}</span>
                {editable && (
                  <>
                    <button
                      onClick={() => {
                        setEditingId(m.id);
                        setEditName(m.name);
                      }}
                      className="text-gray-500 hover:text-blue-400"
                      title="Rename"
                    >
                      <PencilIcon size={13} />
                    </button>
                    <button
                      onClick={() => handleDelete(m.id)}
                      className="text-gray-500 hover:text-red-400"
                      title="Remove"
                    >
                      <TrashIcon size={13} />
                    </button>
                  </>
                )}
              </>
            )}
          </li>
        ))}
      </ul>
      {editable && (
        <form onSubmit={handleAdd} className="mt-1.5 flex gap-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Add member"
            className="min-w-0 flex-1 rounded border border-gray-700 bg-gray-800 px-2 py-0.5 text-sm"
          />
          <button
            type="submit"
            className="rounded bg-blue-600 px-2.5 py-0.5 text-sm hover:bg-blue-500"
          >
            Add
          </button>
        </form>
      )}
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  );
}
