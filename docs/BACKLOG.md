# Ideas & Backlog

Things beyond v1. The top section is actively being worked on; the rest are
ideas, not commitments.

## In progress (v1.1) — `feature/tournament-editing`

Real-use gaps found after v1:

- **Edit/delete participants** — currently you can only add. Allow renaming and
  removing participants while the tournament is still a draft (before the bracket
  is generated).
- **Delete a tournament** — owner can delete their own tournament (and its
  matches/participants).
- **Correct a reported result** — fix a mis-clicked winner. Only allowed when it
  wouldn't corrupt already-played downstream matches (elimination), or always for
  round robin (just recomputes standings).

## Likely future features
- **Deploy it live** — host backend + Postgres (Render/Railway) and frontend
  (Vercel/Netlify) so there's a real URL. Highest resume payoff.
- **Shareable spectator link** — read-only bracket view, no login (reads are
  already public; needs a clean view + "copy link").
- **Match scores** — per-match scores (`score_a`/`score_b`), best-of-N series.
- **Teams** — `Participant.type` already reserves `TEAM`; add roster management.
- **Seeding controls** — manual seeding / drag-to-reorder before generating.
- **Double-elim byes** — support non-power-of-two counts in double elimination.
- **Third-place match** in single-elimination.
- **Tournament templates / presets** for quick recurring game nights.

## Testing & robustness
- **Frontend tests** — none yet; add Vitest + React Testing Library.
- **End-to-end tests** — a Playwright happy-path test through the UI.
- **WebSocket reconnect** — the live feed currently drops if the server blips.

## Nice-to-haves
- Export bracket as image/PDF.
- Match scheduling / time slots for in-person events.
- Basic stats per participant across tournaments.
- README screenshots / demo GIF.
- Dark mode toggle (currently dark-only).

## Bigger / maybe-never
- Public hosting / multi-tenant SaaS.
- Per-participant accounts, profiles, chat.
- Game API integrations for automatic score feeds.
- Mobile app.
