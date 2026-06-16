import { useState } from "react";
import { api } from "../api/client";
import type { Participant } from "../api/types";
import { CheckIcon, CloseIcon, PencilIcon, TrashIcon } from "./icons";
import RosterEditor from "./RosterEditor";

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
  const [isTeam, setIsTeam] = useState(false);
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
        seed.trim() ? Number(seed) : null,
        isTeam ? "TEAM" : "PLAYER"
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
        <span className="text-muted">({participants.length})</span>
      </h2>

      {editable && (
        <form onSubmit={handleAdd} className="mb-4 flex flex-wrap gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={isTeam ? "Team name" : "Participant name"}
            className="flex-1 rounded-lg border bg-bg px-4 py-2 outline-none transition-colors placeholder:text-muted focus:border-accent"
          />
          <input
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="Seed (optional)"
            type="number"
            min="1"
            className="w-36 rounded-lg border bg-bg px-4 py-2 outline-none transition-colors placeholder:text-muted focus:border-accent"
          />
          <label className="flex items-center gap-2 text-sm text-muted">
            <input
              type="checkbox"
              checked={isTeam}
              onChange={(e) => setIsTeam(e.target.checked)}
              className="accent-accent"
            />
            Team
          </label>
          <button
            type="submit"
            className="rounded-lg bg-accent px-5 py-2 font-medium text-accent-fg transition-colors hover:bg-accent-hover"
          >
            Add
          </button>
        </form>
      )}
      {error && <p className="mb-3 text-danger">{error}</p>}

      {participants.length === 0 ? (
        <p className="text-muted">No participants yet.</p>
      ) : (
        <ul className="grid grid-cols-1 items-start gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {sorted.map((p) => (
            <li
              key={p.id}
              className="rounded-lg border bg-surface px-3 py-2 shadow-sm"
            >
              <div className="flex items-center gap-2">
                {editingId === p.id ? (
                  <>
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onKeyDown={(e) =>
                        e.key === "Enter" && handleSaveEdit(p.id)
                      }
                      autoFocus
                      className="min-w-0 flex-1 rounded border bg-bg px-2 py-1 outline-none focus:border-accent"
                    />
                    <button
                      onClick={() => handleSaveEdit(p.id)}
                      className="text-win hover:opacity-80"
                      title="Save"
                    >
                      <CheckIcon />
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-muted hover:text-fg"
                      title="Cancel"
                    >
                      <CloseIcon />
                    </button>
                  </>
                ) : (
                  <>
                    {p.seed != null && (
                      <span className="text-xs font-semibold text-muted">
                        #{p.seed}
                      </span>
                    )}
                    <span className="flex-1 truncate">{p.name}</span>
                    {p.type === "TEAM" && (
                      <span className="rounded bg-accent/15 px-1.5 py-0.5 text-xs font-medium text-accent">
                        Team
                      </span>
                    )}
                    {editable && (
                      <>
                        <button
                          onClick={() => {
                            setEditingId(p.id);
                            setEditName(p.name);
                          }}
                          className="text-muted hover:text-accent"
                          title="Rename"
                        >
                          <PencilIcon />
                        </button>
                        <button
                          onClick={() => handleDelete(p.id)}
                          className="text-muted hover:text-danger"
                          title="Remove"
                        >
                          <TrashIcon />
                        </button>
                      </>
                    )}
                  </>
                )}
              </div>

              {p.type === "TEAM" && (
                <RosterEditor
                  tournamentId={tournamentId}
                  participant={p}
                  editable={editable}
                  onChange={onChange}
                />
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
