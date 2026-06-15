# Decisions & Current-State Assessment

A lightweight decision log so we have a single source of truth and don't
re-litigate or "make things up" later. Newest decisions at the top.

## Decisions (2026-06-15)

1. **Primary goal: depth of engineering.** Quality, tests, CI, clean
   architecture, auth, real-time — over raw feature count. This is a portfolio
   project meant to be resume-ready.
2. **Support all four formats, user-selectable**, but build them in sequence —
   single-elimination to a production standard first, then double-elim,
   round-robin, swiss behind a strategy interface.
3. **Real-time via WebSockets** for live spectator updates.
4. **Local dev only for now.** Docker-compose is planned in the polish phase;
   not hosting publicly yet.
5. **Real personal use is a requirement, not just a portfolio demo.** Will be
   used for online and in-person games with friends. Implications:
   participants are account-free named entries; fast manual result entry;
   low-friction setup. See [PRODUCT.md](PRODUCT.md).
6. **Build vertically, format-by-format,** rather than building all of one layer
   across all formats.

## Tech choices (inherited from the skeleton, kept)

- **Backend:** FastAPI + SQLAlchemy 2.0 + Alembic. Mature, typed, great for a
  clean layered API and a strong portfolio signal.
- **Frontend:** React + TypeScript + Vite + TailwindCSS.
- **DB:** SQLite for dev/tests, PostgreSQL (via docker-compose) as the target.
- **Tooling:** Ruff + Black + Pytest (backend), ESLint + Prettier (frontend).

## Current-state assessment (as of 2026-06-15)

The repo is a **well-structured skeleton, ~5% built.** Good bones, real logic
mostly absent.

**Working / present**
- Clean monorepo layout; models for Tournament, Participant, Match.
- `Match` already models bracket advancement correctly
  (`next_match_id` + `next_match_slot`).
- Alembic initialized; tooling configured.

**Bugs/gaps to fix first (Phase 0)**
- `core/config.py` uses `from pydantic import BaseSettings` — broken on Pydantic
  v2 (moved to `pydantic-settings`, which isn't a declared dependency).
- `db/session.py` hardcodes `sqlite:///./test.db` and ignores
  `settings.database_url`.
- `frontend/package.json` pins non-existent versions
  (`tailwindcss ^4.3.0`, `postcss ^9.3.0`) and lacks `@vitejs/plugin-react` —
  `npm install` fails as-is.
- `services/bracket.py` is empty placeholders (`pass`).
- No API routes, Pydantic schemas, CRUD layer, or tests yet.
- `Participant` is not scoped to a tournament (no `tournament_id`).

See [ROADMAP.md](ROADMAP.md) for the plan to close these.
