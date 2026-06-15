# Domain Model

This describes the current and planned data model. The current models live in
`backend/app/models/`. Fields marked _(planned)_ don't exist yet.

## Entities

### Tournament
The top-level container for a competition.

| field      | type                | notes |
|------------|---------------------|-------|
| id         | int, PK             | |
| name       | string, required    | |
| status     | enum                | `DRAFT` → `ONGOING` → `COMPLETED` |
| format     | enum                | `SINGLE_ELIM`, `DOUBLE_ELIM`, `ROUND_ROBIN`, `SWISS` (default `SINGLE_ELIM`) |
| owner_id   | int, nullable       | FK to User once auth exists; reserved now |
| created_at | datetime _(planned)_| |

### Participant
A competitor in a tournament. **Not a user account** — just a named entry the
organizer adds. Supports the "in-person games with friends" use case where
players don't log in.

| field          | type             | notes |
|----------------|------------------|-------|
| id             | int, PK          | |
| name           | string, required | |
| type           | string           | `PLAYER` (default) or `TEAM` later |
| tournament_id  | int, FK          | scopes the participant to its tournament |
| seed           | int, nullable    | lower = stronger; drives bracket seeding |

### Match
A single game between two participants, and its place in the bracket.

| field           | type                | notes |
|-----------------|---------------------|-------|
| id              | int, PK             | |
| tournament_id   | int, FK             | |
| round_number    | int, required       | which round of the bracket |
| player_a_id     | int, FK participant | nullable until filled by advancement |
| player_b_id     | int, FK participant | nullable until filled by advancement |
| winner_id       | int, FK, nullable   | set when result is reported |
| next_match_id   | int, FK match, null | where the winner goes next |
| next_match_slot | enum `A`/`B`, null  | which slot of the next match the winner fills |
| score_a         | int, nullable _(planned)_ | optional score tracking |
| score_b         | int, nullable _(planned)_ | optional score tracking |

The `next_match_id` + `next_match_slot` pair is the mechanism for bracket
advancement: reporting a winner writes that participant into the correct slot of
the downstream match. This is already modeled correctly.

### User _(planned — Phase 3)_
An organizer who can log in and own tournaments. Participants are **not** users.

| field           | type             | notes |
|-----------------|------------------|-------|
| id              | int, PK          | |
| email           | string, unique   | |
| hashed_password | string           | |
| created_at      | datetime         | |

### Team _(future)_
A group of players competing as one participant. Deferred — `Participant.type`
already reserves room for `TEAM`.

## Relationships

- A **Tournament** has many **Participants** and many **Matches**.
- A **Match** references two **Participants** (a/b) and an optional winner.
- A **Match** optionally points to a downstream **Match** (`next_match_id`).
- A **User** (future) owns many **Tournaments** via `owner_id`.

## Format-specific notes

- **Single / double elimination** rely on the match-tree wiring above.
- **Round-robin / swiss** are not pure trees — they need standings derived from
  results (wins/losses/points). The engine's `standings()` method
  (see [ARCHITECTURE.md](ARCHITECTURE.md)) covers this; a dedicated standings or
  results table may be added when those formats are built.
