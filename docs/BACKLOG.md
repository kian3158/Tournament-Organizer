# Backlog

Where the project might go next, plus a record of what's already shipped past the
first version. None of the "later" stuff is a commitment.

## Already done past v1

Editing a draft (rename, remove, or reorder players by dragging, delete a whole
tournament) and fixing a mis-clicked result after the fact. Match scores with
best-of-3/5/7. Teams that carry a roster. An optional third-place match for
single elimination, and byes in double elimination for odd player counts. A
read-only spectator link with a live feed that reconnects on its own. Quick
presets in the create form. PNG export of a bracket or standings table. A stats
page with each participant's record across tournaments. Light/dark themes with a
pickable accent color. And a frontend test suite (Vitest) running in CI.

## Might do next

- **Deploy it live** so there's a real URL — backend and Postgres on something
  like Render or Railway, frontend on Vercel or Netlify.
- **End-to-end test** — one Playwright run through the main happy path.
- **Match scheduling** — time slots for in-person events.

## Probably not

Public multi-tenant hosting, per-participant accounts and social features,
automatic score feeds from game APIs, and a native mobile app. Fun to imagine,
out of scope for what this is.
