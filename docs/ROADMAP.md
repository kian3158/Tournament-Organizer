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

## Phase 2 — Bracket UI
Make it visible and usable.

- [ ] Typed API client.
- [ ] Tournament list + create; participant management.
- [ ] **Bracket visualization** (rounds → matches), click-to-report-winner for
      the organizer, fast manual entry (in-person friendly).

## Phase 3 — Auth & multi-user
Organizers own their tournaments. Participants stay account-free.

- [ ] User model, registration/login, JWT, password hashing.
- [ ] Tie `Tournament.owner_id` to the logged-in user; protect mutations.
- [ ] Frontend auth flow (login/register, authed requests).

## Phase 4 — Real-time (WebSockets)
Live spectating.

- [ ] WebSocket channel per tournament; broadcast on result changes.
- [ ] Frontend subscribes and updates the bracket live (optimistic UI).

## Phase 5 — More formats (breadth, on a solid base)
Refactor to a clean strategy interface, then add one at a time, each fully
tested:

- [ ] Extract `TournamentFormat` interface; make single-elim an implementation.
- [ ] **Double-elimination** (losers bracket — the hardest).
- [ ] **Round-robin** (standings/points).
- [ ] **Swiss** (record-based pairing).
- [ ] Let the user pick the format at tournament creation.

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

Currently at: **Phase 2 — Bracket UI (next).**
