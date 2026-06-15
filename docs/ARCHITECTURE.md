# Architecture

## Overview

Monorepo with a Python backend and a React frontend in one repository.

```
Tournament/
├── backend/          FastAPI + SQLAlchemy + Alembic
│   └── app/
│       ├── core/        config / settings
│       ├── db/          engine, session, Base
│       ├── models/      SQLAlchemy ORM models
│       ├── schemas/     Pydantic request/response models   (to be added)
│       ├── crud/        DB access helpers                   (to be added)
│       ├── services/    business logic (bracket engine)
│       ├── api/         FastAPI routers / endpoints          (to be added)
│       └── main.py      app entrypoint
├── frontend/         React + TypeScript + Vite + TailwindCSS
└── docs/             source of truth for product & engineering decisions
```

## Layering (backend)

Strict, one-directional dependency flow. This separation is deliberate and is
part of the "depth of engineering" story:

```
api (routers)  →  services  →  crud  →  models / db
        ↘         schemas (Pydantic)  ↗
```

- **api** — thin. Parses/validates input (via schemas), calls a service or crud,
  returns a schema. No business logic here.
- **services** — business logic. The bracket engine lives here. Knows nothing
  about HTTP.
- **crud** — database reads/writes. Knows nothing about brackets or HTTP.
- **models** — SQLAlchemy ORM tables.
- **schemas** — Pydantic models for the API boundary (separate from ORM models).

Rule of thumb: **bracket logic lives in services, never in routes.**

## The tournament engine (key design)

The product supports multiple formats (single-elim, double-elim, round-robin,
swiss). To keep this clean and testable, formats are implemented behind a common
**strategy interface** rather than branching logic scattered everywhere.

```
TournamentFormat (interface)
├── generate(tournament, participants) -> creates matches
├── advance(match, winner)             -> propagates result, updates state
└── standings(tournament)              -> current ranking (esp. round-robin/swiss)

implementations:
├── SingleEliminationFormat   (built first, to production standard)
├── DoubleEliminationFormat
├── RoundRobinFormat
└── SwissFormat
```

A tournament stores which format it uses; the service layer dispatches to the
right strategy. Adding a format = adding a class + tests, not rewriting the API
or UI.

## Real-time (WebSockets)

Spectators get live updates. When a result is reported via REST:

1. The service updates the bracket in the DB.
2. The server broadcasts the changed bracket state over a WebSocket channel
   scoped to that tournament (e.g. `/ws/tournaments/{id}`).
3. Connected frontend clients apply the update without refreshing.

REST remains the source of truth for mutations; WebSockets are a push channel for
read updates. This keeps the system simple to reason about and test.

## Frontend

- React + TypeScript, built with Vite, styled with TailwindCSS.
- A typed API client wraps the backend REST endpoints.
- A WebSocket client subscribes to a tournament for live bracket updates.
- The bracket visualization is the centerpiece component: rounds → matches, with
  click-to-report-winner for organizers.

## Data store

- **Development:** SQLite (zero-setup, good for fast local iteration and tests).
- **Target:** PostgreSQL via docker-compose (matches a production-style setup).
- Schema changes are managed with **Alembic** migrations — never auto-create
  tables in production code paths.

## Quality / tooling

- Backend: Ruff (lint) + Black (format) + Pytest (tests).
- Frontend: ESLint + Prettier.
- CI (GitHub Actions): lint + tests on every push (added in the polish phase).

See [DECISIONS.md](DECISIONS.md) for why these choices were made.
