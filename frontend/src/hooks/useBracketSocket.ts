import { useEffect } from "react";
import { bracketSocketUrl } from "../api/client";
import type { Bracket } from "../api/types";

/**
 * Subscribe to live bracket updates for a tournament. The server pushes a
 * snapshot on connect and a fresh bracket whenever a result is reported.
 *
 * Reconnects automatically with exponential backoff if the socket drops (server
 * restart, network blip), and stops once the component unmounts.
 */
export function useBracketSocket(
  tournamentId: number,
  onUpdate: (bracket: Bracket) => void
) {
  useEffect(() => {
    if (!Number.isFinite(tournamentId)) return;

    let closed = false;
    let socket: WebSocket | null = null;
    let retry = 0;
    let timer: ReturnType<typeof setTimeout> | undefined;

    function connect() {
      socket = new WebSocket(bracketSocketUrl(tournamentId));
      socket.onmessage = (event) => {
        try {
          onUpdate(JSON.parse(event.data) as Bracket);
        } catch {
          // ignore malformed frames
        }
      };
      socket.onopen = () => {
        retry = 0;
      };
      socket.onclose = () => {
        if (closed) return;
        const delay = Math.min(1000 * 2 ** retry, 15000);
        retry += 1;
        timer = setTimeout(connect, delay);
      };
    }

    connect();
    return () => {
      closed = true;
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [tournamentId, onUpdate]);
}
