# Issue tracker: GitHub Issues

Issues live in GitHub Issues for `alepocalypse/Dreamlight-HUD`. Use the `gh` CLI (`gh issue list/view/create/comment/close`).

## Conventions

- One ticket per issue. Specs and larger write-ups go in the issue body, or in `docs/` if they should live with the code.
- Triage state is a label (see `triage-labels.md`). Feature areas are also labels (e.g. `architecture`, `event-duties`).
- Blocking is written in the body as `Blocked by: #N`.
- Comments and conversation go in the issue's comments.

## When a skill says "publish to the issue tracker"

`gh issue create` with a title, body and the relevant labels.

## When a skill says "fetch the relevant ticket"

`gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is an issue labelled `map`; each **child** is an issue that references it.

- **Map**: issue labelled `map` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: an issue with `Map: #N` and a `Type:` line (`research`/`prototype`/`grilling`/`task`) in the body; the `claimed` label marks it taken, closing it marks it resolved.
- **Blocking**: a `Blocked by: #N, #N` line. A ticket is unblocked when every listed issue is closed.
- **Frontier**: open, unblocked, unclaimed children of the map; lowest number wins.
- **Claim**: add the `claimed` label before any work.
- **Resolve**: comment the answer under an `## Answer` heading, close the issue, then append a context pointer (gist + link) to the map's Decisions-so-far.
