# Security Policy

## Scope

Dreamlight HUD is a local, read-only tool. It reads your save file, serves a page only to
`127.0.0.1`, and makes no network requests of its own. Reports about anything that breaks those
properties (writing to the game folder, exposing the page beyond your own machine, unsafe handling of
a crafted save file) are in scope.

## Reporting a vulnerability

Please report privately through GitHub:
[Report a vulnerability](../../security/advisories/new). Do not open a public issue for it.

This is a hobby project maintained by one person, so expect a reply within about a week. Fixes go into
the next release, and you will be credited if you want to be.

## Supported versions

Only the [latest release](../../releases/latest) receives fixes.
