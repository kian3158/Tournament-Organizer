# Architecture

One repo, two halves: a FastAPI backend and a React frontend.

```
Tournament/
├── backend/          FastAPI + SQLAlchemy + Alembic
│   └── app/
│       ├── core/        config / settings
│       ├── db/          engine, session, Base
│       ├── models/      SQLAlchemy ORM models
│       ├── schemas/     Pydantic request/response models
│       ├── crud/        DB access helpers
│       ├── services/    business logic (bracket engine + formats/)
│       ├── api/         FastAPI routers / endpoints
│       ├── tests/       pytest suite (algorithm, service, API)
│       └── main.py      app entrypoint
├── frontend/         React + TypeScript + Vite + Tailwind
└── docs/             product notes, architecture, backlog
```

## Backend layers

Dependencies flow one way: routers call services and crud, services own the
business logic, crud talks to the database, and Pydantic schemas sit at the API
boundary.

```
api (routers)  →  services  →  crud  →  models / db
        ↘         schemas (Pydantic)  ↗
```

Routers stay thin — they validate input with a schema, call a service or crud
function, and return a schema. The bracket logic lives in services and never in
a route. crud knows about the database but nothing about brackets or HTTP.

## The tournament engine

The interesting part is bracket generation, and all four formats share one
interface so the logic doesn't sprawl into branching everywhere:

```
FormatStrategy (services/formats/base.py)
└── build(participant_ids) -> list[MatchPlan]

SingleEliminationFormat
DoubleEliminationFormat
RoundRobinFormat
SwissFormat
```

`build()` is pure: it returns `MatchPlan` objects with local indices and
next-match pointers and touches no database, which makes the seeding and pairing
math straightforward to unit-test on its own. `BracketService`
(`services/bracket.py`) takes those plans, writes the `Match` rows, wires up the
self-referential `next_match_id` links, auto-advances byes, and handles result
reporting and completion.

A tournament stores its format as the `TournamentFormat` enum; the service looks
up the matching `FormatStrategy` and runs it. Adding a format means writing a new
strategy class and its tests, not changing the API or the UI.

## Real-time updates

When a result is reported over REST, the service writes it to the database and
then broadcasts the new bracket state over a WebSocket channel scoped to that
tournament (`/ws/tournaments/{id}`). Connected clients apply the update without
refreshing. REST stays the source of truth for changes; the socket is just a push
channel for reads, which keeps things easy to reason about.

## Frontend

React and TypeScript, built with Vite and styled with Tailwind. A typed client
wraps the REST endpoints, and a small hook subscribes to the WebSocket for live
bracket updates. The bracket view is the centerpiece — rounds and matches with
click-to-report-winner for the organizer. Component and API-client tests run on
Vitest.

## Data and tooling

Local development uses SQLite for zero setup; Docker Compose runs Postgres to
match a more production-like environment. Schema changes go through Alembic
migrations rather than auto-created tables. The backend is linted with ruff and
formatted with black, and CI runs both test suites plus the build on every push.
