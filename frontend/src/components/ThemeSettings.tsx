import { useEffect, useRef, useState } from "react";
import { CogIcon } from "./icons";

const ACCENTS = [
  { id: "purple", label: "Purple", swatch: "#7c6cff" },
  { id: "red", label: "Red", swatch: "#dc2626" },
  { id: "orange", label: "Orange", swatch: "#ea580c" },
  { id: "green", label: "Green", swatch: "#16a34a" },
  { id: "blue", label: "Blue", swatch: "#2563eb" },
  { id: "bloodborne", label: "Bloodborne", swatch: "#961616" },
];

function currentAccent(): string {
  return document.documentElement.dataset.accent || "purple";
}

export default function ThemeSettings() {
  const [open, setOpen] = useState(false);
  const [accent, setAccent] = useState(currentAccent);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (accent === "purple") delete document.documentElement.dataset.accent;
    else document.documentElement.dataset.accent = accent;
    localStorage.setItem("accent", accent);
  }, [accent]);

  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="rounded-md border p-1.5 text-muted transition-colors hover:bg-elevated hover:text-fg"
        title="Theme settings"
        aria-label="Theme settings"
      >
        <CogIcon />
      </button>
      {open && (
        <div className="absolute right-0 z-50 mt-2 w-44 rounded-lg border bg-surface p-3 shadow-lg">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
            Accent
          </p>
          <div className="flex flex-wrap gap-2">
            {ACCENTS.map((a) => (
              <button
                key={a.id}
                onClick={() => setAccent(a.id)}
                title={a.label}
                aria-label={a.label}
                style={{ backgroundColor: a.swatch }}
                className={`h-6 w-6 rounded-full ring-2 ring-offset-2 ring-offset-surface transition ${
                  accent === a.id ? "ring-fg" : "ring-transparent"
                }`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
