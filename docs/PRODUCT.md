# Product notes

A tournament organizer for esports and LAN-style game nights. You create a
tournament, add participants, generate a bracket, and report results as matches
are played. The app advances winners on its own until there's a champion, and
spectators can follow along live.

## What shapes the design

It's built to actually run game nights with friends, online and in person, and
that drives a few choices.

Participants don't have accounts. The organizer just adds them by name — a
participant is a label in a bracket, not a logged-in user. Accounts exist only
for the organizers who own tournaments.

Reporting results by hand is the main flow, not a fallback. In-person games have
no automatic score feed, so the organizer clicks the winner of each match. That
has to be quick and hard to get wrong, and setup has to be fast too, since it
usually happens live with people waiting to play.

Having several formats matters because different groups play differently:
single elimination for a quick night, round robin for an everyone-plays-everyone
league, and so on.

## A typical run

1. Create a tournament and add the players.
2. Generate the bracket. The app seeds players, fills in byes when the count
   isn't a power of two, and wires all the matches together.
3. Report each match's winner as games finish. Winners advance automatically and
   byes resolve themselves.
4. The bracket updates live for anyone watching, and the tournament is marked
   complete once there's a champion.

## Not doing (for now)

Public hosting or multi-tenant SaaS, per-participant accounts and social
features, payments, and game-specific score integrations. Some of these may end
up in [BACKLOG.md](BACKLOG.md) later.
