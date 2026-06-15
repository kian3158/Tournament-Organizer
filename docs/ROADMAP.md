# Roadmap

**Goal:** depth of engineering — a polished, production-style app that's
resume-ready, while also being genuinely usable for personal tournaments
(online and in-person). See [PRODUCT.md](PRODUCT.md).

**Strategy:** build *vertically*. Take single-elimination all the way from DB →
service → API → tests → UI → live updates to a production standard first. Then
add the other formats on that solid base behind a strategy interface
(see [ARCHITECTURE.md](ARCHITECTURE.md)). Quality of the first slice > number of
half-finished formats.

Each phase ends with a clean, committed, verifiably-working state.

---

## Phase 0 — Make it run (fix the skeleton)
Get a green baseline. Nothing can be built or shown until this is solid.

- [ ] Fix `core/config.py` to use `pydantic-settings` (Pydantic v2 compatible).
- [ ] Make `db/session.py` read the DB URL from settings instead of hardcoding.
- [ ] Add `pydantic-settings` to backend deps; confirm Poetry install works.
- [ ] Fix `frontend/package.json` to real dependency versions; add
      `@vitejs/plugin-react`; wire Tailwind correctly.
- [ ] Confirm `uvicorn` backend boots and `npm run dev` frontend boots.
- [ ] First Alembic migration that actually creates the tables; confirm it runs.
- [ ] Commit a clean baseline.

## Phase 1 — Tournament engine: single-elimination (the core) ✅ DONE
The algorithmically interesting heart of the app.

- [x] Add `tournament_id` (and `seed`) to `Participant`.
- [x] Add `format` to `Tournament`.
- [x] Pydantic schemas + a thin CRUD layer.
- [x] `SingleEliminationFormat.build()` — seeding + byes for non-power-of-two
      participant counts.
- [x] `advance()` — propagate winner via `next_match_id`/`next_match_slot`,
      auto-resolve byes, complete the tournament when the final is decided.
- [x] REST endpoints: create tournament, add participants, generate bracket,
      report result, get full bracket state.
- [x] **Thorough unit tests** on the bracket math: 2/4/5/8/16 players, odd
      counts, byes, full run-through to a champion (38 tests across the pure
      algorithm, the service, and the API).

## Phase 2 — Bracket UI ✅ DONE
Make it visible and usable.

- [x] Typed API client (`frontend/src/api/`), CORS enabled on the backend.
- [x] Tournament list + create; participant management (name + optional seed).
- [x] **Bracket visualization** (rounds → matches, round labels, byes/TBD,
      champion banner), click-to-report-winner for the organizer.
- Verified end to end in the browser, including a 10-player bracket with byes
  played through to a champion.

## Phase 3 — Auth & multi-user ✅ DONE
Organizers own their tournaments. Participants stay account-free.

- [x] User model, registration/login, JWT (PyJWT), password hashing (bcrypt).
- [x] Tie `Tournament.owner_id` to the logged-in user; mutations require
      ownership (create/add-participant/generate/report); reads stay public so
      brackets are shareable. Listing is scoped to the current user.
- [x] Frontend auth flow: auth context, login/register page, token in
      localStorage, route guard, and organizer-only controls.
- 50 backend tests (incl. auth + ownership); verified in-browser.

## Phase 4 — Real-time (WebSockets) ✅ DONE
Live spectating.

- [x] WebSocket channel per tournament (`/ws/tournaments/{id}`); snapshot on
      connect, broadcast on generate + result changes (`ConnectionManager`).
- [x] Frontend subscribes (`useBracketSocket`) and updates the bracket live.
- Verified in-browser: a reported result is pushed to a connected client.

## Phase 5 — More formats (breadth, on a solid base)
Add one at a time on the `FormatStrategy` interface, each fully tested:

- [x] `FormatStrategy` interface; single-elim as an implementation (Phase 1).
- [x] **Double-elimination** — winners + losers brackets, grand final with
      bracket reset. Loser-routing added to the `Match` model; bracket-aware
      frontend rendering. Power-of-two only for now (byes → backlog). Verified
      in-browser (winner advances, loser drops, reset path tested).
- [x] Let the user pick the format at tournament creation.
- [ ] **Round-robin** (standings/points).
- [ ] **Swiss** (record-based pairing).

## Phase 6 — Production polish (the resume payoff)
- [ ] `docker-compose` for the full stack (incl. PostgreSQL).
- [ ] GitHub Actions CI: lint + tests on every push.
- [ ] Test coverage reporting.
- [ ] Strong README: screenshots/GIF, architecture write-up, run instructions.
- [ ] OpenAPI docs polished.

---

## Status

- **Phase 0 — done.** Foundation runs (backend + frontend boot, migrations apply).
- **Phase 1 — done.** Single-elimination engine complete end to end: layered
  backend (models → services → crud → schemas → api), pure seeding/bye algorithm,
  bracket generation + result reporting + auto-completion, and 38 passing tests.
- **Phase 2 — done.** React UI: tournament list/create, participant management,
  and an interactive bracket with click-to-report-winner. Verified in-browser.
- **Phase 3 — done.** JWT auth (register/login), bcrypt hashing, tournaments
  owned by users with ownership-protected mutations, and a frontend auth flow.
- **Phase 4 — done.** WebSocket channel per tournament; the server pushes live
  bracket updates on generate/result, and the frontend subscribes for live
  spectating. Verified in-browser.
- **Phase 5 — in progress.** Double-elimination done (winners/losers brackets +
  grand-final reset, format picker at creation, bracket-aware UI). Round-robin
  and swiss still to come.

Currently at: **Phase 5 — round-robin next.**
