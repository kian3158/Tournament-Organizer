import { useEffect } from "react";
import { bracketSocketUrl } from "../api/client";
import type { Bracket } from "../api/types";

/**
 * Subscribe to live bracket updates for a tournament. The server pushes a
 * snapshot on connect and a fresh bracket whenever a result is reported.
 */
export function useBracketSocket(
  tournamentId: number,
  onUpdate: (bracket: Bracket) => void
) {
  useEffect(() => {
    if (!Number.isFinite(tournamentId)) return;
    const socket = new WebSocket(bracketSocketUrl(tournamentId));
    socket.onmessage = (event) => {
      try {
        onUpdate(JSON.parse(event.data) as Bracket);
      } catch {
        // ignore malformed frames
      }
    };
    return () => socket.close();
  }, [tournamentId, onUpdate]);
}
