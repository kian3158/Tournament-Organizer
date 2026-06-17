# Tournament Organizer

![CI](https://github.com/kian3158/Tournament-Organizer/actions/workflows/ci.yml/badge.svg)

A web app for running game-night and esports tournaments. Make a tournament, add
players, pick a format, and click the winner as each game finishes. It builds the
bracket, keeps score, and pushes updates live to anyone watching.


## Formats

- **Single elimination** with seeding and byes for any number of players.
- **Double elimination** with a losers bracket, a grand-final reset, and byes
  for any player count.
- **Round robin** where everyone plays everyone, ranked in a standings table.
- **Swiss** that pairs players on similar records each round and avoids rematches.

## Features

- **Run a bracket live** — click the winner of each game and the bracket fills
  in; spectators watch it update in real time.
- **Match scores & best-of-N** — record game scores and set matches to best of
  1, 3, 5, or 7.
- **Editing & corrections** — rename or remove participants, delete tournaments,
  and fix a mis-clicked result (it re-propagates downstream when that's safe).
- **Seeding** — type seeds or drag participants to reorder them.
- **Teams** — a participant can be a team with a managed roster.
- **Third-place match** — optional for single elimination.
- **Spectator link** — a read-only `/watch/:id` view that needs no login.
- **Light & dark theme** — toggle in the header, remembered across visits.

## Screenshots

<!-- Drop captures into docs/screenshots/ and uncomment:
![Bracket](docs/screenshots/bracket-dark.png)
![Standings](docs/screenshots/standings-light.png)
-->

_Screenshots live in [`docs/screenshots/`](docs/screenshots/)._

## Stack

Backend is FastAPI + SQLAlchemy + Postgres (SQLite locally), with Alembic
migrations and JWT auth. Frontend is React + TypeScript + Vite + Tailwind. Live
updates run over WebSockets. Tests are pytest, linting is ruff/black, CI is
GitHub Actions, and the whole thing runs in Docker.

## Running it

### Docker

```bash
docker compose up --build
```

Frontend on http://localhost:5173, API docs on http://localhost:8000/docs. This
starts Postgres, runs migrations, and serves everything.

### Locally

Backend (Python 3.11+, Poetry):

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

The frontend calls http://localhost:8000 by default; set `VITE_API_BASE_URL` to
change it.

## Tests

```bash
cd backend
poetry run pytest --cov=app
```

Around 145 tests covering the bracket math for all four formats, scoring and
seeding, the API, auth, and the live feed.

## How it's put together

Bracket logic lives in the service layer behind a small `FormatStrategy`
interface, so each format is its own piece and adding one doesn't touch the API
or UI. The pairing and seeding math is plain functions with no database in them,
which keeps it easy to test. There's a longer write-up in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
api  ->  services (bracket engine + formats)  ->  crud  ->  models / db
```

## Project layout

```
backend/    FastAPI app (api / services / crud / schemas / models), Alembic, tests
frontend/   React + TS app (pages / components / api client / auth / hooks)
docs/       product, architecture, domain model, roadmap, decisions, backlog
```

## Docs

- [Product](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/DOMAIN_MODEL.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisions](docs/DECISIONS.md)
- [Backlog](docs/BACKLOG.md)

## Notes

- All four formats handle any number of players; elimination brackets pad up to
  a power of two with byes.
- Change `SECRET_KEY` before deploying anywhere real; the default is just for local.

## License

[MIT](LICENSE) © kian3158
