# 🏆 Tournament Organizer

![CI](https://github.com/kian3158/Tournament-Organizer/actions/workflows/ci.yml/badge.svg)

A full-stack tournament organizer for esports and LAN-style competitions. Create
a tournament, add participants, generate a bracket, and report results as games
are played — the app advances winners automatically and updates every spectator
live. Built for real use at game nights (online and in person) as well as to
demonstrate end-to-end engineering.

## Features

- **Four tournament formats**, selectable per tournament:
  - **Single elimination** — seeding and byes for any participant count.
  - **Double elimination** — winners + losers brackets and a grand final with
    bracket reset.
  - **Round robin** — everyone plays everyone, ranked by a standings table.
  - **Swiss** — record-based pairing generated round by round, avoiding rematches.
- **Automatic bracket logic** — winners advance, losers drop (double-elim), byes
  resolve themselves, and the tournament completes when the result is decided.
- **Live updates** — spectators see results the moment they're reported, over
  WebSockets (no refresh).
- **Organizer accounts** — register/login with JWT auth; you manage your own
  tournaments. Participants stay account-free (just names), so setup is fast.
- **Fast manual result entry** — click a player to record the win, designed for
  running games live.

## Tech stack

| Layer    | Tech |
|----------|------|
| Backend  | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PyJWT, bcrypt |
| Frontend | React 18, TypeScript, Vite, TailwindCSS, React Router |
| Realtime | WebSockets (Starlette / `websockets`) |
| Database | PostgreSQL (Docker), SQLite (local dev/tests) |
| Tooling  | Ruff, Black, Pytest (+coverage), ESLint-ready, Docker, GitHub Actions |

## Architecture

A layered monorepo. Bracket logic lives in the service layer behind a
`FormatStrategy` interface, so each format is a self-contained, unit-tested
strategy — adding a format doesn't touch the API or UI.

```
api (routers)  →  services (bracket engine + formats/)  →  crud  →  models / db
        ↘                schemas (Pydantic)             ↗
```

The bracket math (seeding, byes, double-elim drop routing, swiss pairing) is
written as **pure functions** that return DB-agnostic match plans, which the
service then persists — which is why it's testable in isolation and has ~98%
coverage. Full write-up in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Getting started

### With Docker (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

This starts PostgreSQL, runs database migrations, and serves the API and the
built frontend.

### Local development

**Backend** (Python 3.11+, Poetry):

```bash
cd backend
poetry install
poetry run alembic upgrade head      # creates the SQLite dev DB
poetry run uvicorn app.main:app --reload
```

**Frontend** (Node 20+):

```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

The frontend talks to `http://localhost:8000` by default; override with
`VITE_API_BASE_URL`.

## Tests

```bash
cd backend
poetry run pytest --cov=app --cov-report=term-missing
```

100+ tests covering the bracket algorithms (all four formats, byes, reset,
rematch avoidance), the service/persistence layer, the REST API, auth/ownership,
and the WebSocket feed.

## Project layout

```
backend/    FastAPI app (api / services / crud / schemas / models), Alembic, tests
frontend/   React + TS app (pages / components / api client / auth / hooks)
docs/       product, architecture, domain model, roadmap, decisions, backlog
```

## Documentation

- [Product vision](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Roadmap & status](docs/ROADMAP.md)
- [Decisions & current state](docs/DECISIONS.md)
- [Backlog](docs/BACKLOG.md)

## Notes & limitations

- Double elimination currently requires a power-of-two participant count; byes
  for other counts are on the [backlog](docs/BACKLOG.md). The other three formats
  handle any count.
- Set a strong `SECRET_KEY` (32+ random bytes) in any real deployment; the
  default is a development placeholder.

## License

[MIT](LICENSE) © Kian Shahrami
