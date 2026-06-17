# Ideas & Backlog

Things beyond v1. The top section is actively being worked on; the rest are
ideas, not commitments.

## Done in v1.1 — `feature/tournament-editing`

Shipped on this branch (editing gaps found after v1, plus the next batch of
real features):

- [x] **Edit/delete participants** — rename or remove participants while the
  tournament is still a draft (before the bracket is generated).
- [x] **Delete a tournament** — owner can delete their own tournament (and its
  matches/participants).
- [x] **Correct a reported result** — fix a mis-clicked winner; re-propagates
  downstream. Blocked when a later dependent match is already decided, or for
  the grand final / locked swiss rounds. Always safe for round robin.
- [x] **Match scores** — optional per-match scores (e.g. 2-1), validated against
  the winner and shown in the bracket. Corrections swap scores to follow the
  new winner.
- [x] **Shareable spectator link** — read-only, login-free `/watch/:id` view
  with live updates, plus a "Share" button that copies the link.
- [x] **Double-elim byes** — double elimination now pads non-power-of-two counts
  with byes; the losers bracket passes lone droppers through (no empty matches).
- [x] **Teams with rosters** — a participant can be a team with managed member
  names (add/rename/remove in draft), shown with a Team badge.

## Done in v1.2 — `feature/bestof-seeding-thirdplace`

- [x] **Best-of-N** — matches can be best of 1/3/5/7; scores are validated
  against the majority needed to win.
- [x] **Manual seeding** — drag participants to reorder; seeds are assigned by
  position (plus a bulk reorder endpoint).
- [x] **Third-place match** — optional extra match between the semifinal losers
  in single elimination.
- [x] **Light / dark theme** — header toggle backed by semantic color tokens,
  remembered across visits.

## Done in v1.3 — `feature/tests-and-extras`

- [x] **Frontend tests** — Vitest + React Testing Library (component + API-client
  tests), wired into CI.
- [x] **WebSocket reconnect** — the live feed reconnects with backoff after a drop.
- [x] **Tournament presets** — one-click setups in the create form.
- [x] **Export bracket as PNG** — via html2canvas, from the bracket/standings view.
- [x] **Per-participant stats** — win/loss/title records aggregated by name across
  the owner's tournaments, on a `/stats` page.

## Likely future features
- **Deploy it live** — host backend + Postgres (Render/Railway) and frontend
  (Vercel/Netlify) so there's a real URL. Highest resume payoff.

## Testing & robustness
- **End-to-end tests** — a Playwright happy-path test through the UI.

## Nice-to-haves
- Export bracket as image/PDF.
- Match scheduling / time slots for in-person events.
- Basic stats per participant across tournaments.
- README screenshots / demo GIF.

## Bigger / maybe-never
- Public hosting / multi-tenant SaaS.
- Per-participant accounts, profiles, chat.
- Game API integrations for automatic score feeds.
- Mobile app.
