# Contributing

Thanks for helping. Bug reports, save-file samples that show a case the HUD gets wrong, and pull
requests are all welcome.

## Reporting a problem

Open an [issue](../../issues/new/choose). Say what you expected, what the HUD showed, and your
platform. **Do not attach your raw save file or profile.json**; describe what is wrong, or
see below for how to share a report safely.

## Changing the code

    python3 -m unittest discover -s tests

- Run the tests before opening a pull request, and add one for new behavior.
- The app only ever reads the save. A test fails if code tries to write to the game folder; keep it that way.
- Use the terms in [`GLOSSARY.md`](../GLOSSARY.md) (Villager, Companion, Star Path, and so on) in code, UI text, and docs.
- Decisions with lasting consequences are recorded in `docs/adr/`.
- For UI changes, look at the result: `python3 tools/screenshot.py --demo` writes screenshots you can check.
- Keep pull requests small and focused on one change.

## Licensing

Code contributions are under the project's MIT license. Do not add Disney or Gameloft artwork beyond
what is already in `ddvhud/static/`.
