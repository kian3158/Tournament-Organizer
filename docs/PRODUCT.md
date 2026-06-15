# Product Vision

## What it is

A full-stack tournament organizer for esports and LAN-style competitions. You
create a tournament, add participants, generate a bracket, report results as
matches are played, and the app advances winners automatically until there's a
champion. Spectators can follow the bracket live.

## Who it's for

1. **Hiring managers / resume reviewers** — this is a portfolio project meant to
   demonstrate depth of engineering: clean architecture, tests, CI, auth,
   real-time features, and a polished UI. See [ROADMAP.md](ROADMAP.md).
2. **The author and friends (real usage)** — it will actually be used to run
   personal tournaments, for both:
   - **Online games** — participants are remote; results entered by whoever is
     organizing or playing.
   - **In-person / LAN games** — board games, console nights, etc. The organizer
     runs everything from one screen and types in results.

## What this means for design

The "personal use with friends" use case drives some important decisions:

- **Participants don't need accounts.** The organizer adds participants by name.
  A participant is just a label in a bracket, not a logged-in user. (Auth, when
  added, is for *organizers* who own tournaments — not for every player.)
- **Manual result entry is a first-class flow,** not an afterthought. In-person
  games have no automatic score feed; the organizer reports the winner of each
  match. This must be fast and hard to get wrong.
- **Low-friction setup.** Creating a tournament and getting to a usable bracket
  should take seconds, because it'll be done live with friends waiting.
- **Multiple formats matter** because friend groups play different things:
  single-elim for quick nights, round-robin for "everyone plays everyone"
  league nights, etc.

## Core user journey (single-elimination, the first format)

1. Organizer creates a tournament (name).
2. Organizer adds participants (names).
3. Organizer generates the bracket — the app seeds players, inserts byes if the
   count isn't a power of two, and creates all matches wired together.
4. As games are played, the organizer reports each match's winner.
5. Winners auto-advance to the next match; byes auto-resolve.
6. The bracket updates live for anyone watching; eventually a champion is set and
   the tournament is marked complete.

## Non-goals (for now)

- Public hosting / multi-tenant SaaS (running locally for now).
- Per-participant accounts, chat, or social features.
- Payments, ticketing, or anything commercial.
- Game-specific integrations (auto score feeds from game APIs).

These may move into the backlog later — see [BACKLOG.md](BACKLOG.md).
