## Agent skills

### Issue tracker

Issues are GitHub Issues (`alepocalypse/Dreamlight-HUD`, use `gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Seeing the page

For any UI change, look at the result; do not report rendering as unverified. Run:

    python3 tools/screenshot.py [--demo | --report FILE.json] [--width N] [--scheme light|dark|both] [--out DIR]

It re-runs itself under `.venv/bin/python` (Playwright + headless Chromium), starts its own app server on a free port (never touch the user's server on 8798 or their Firefox), and writes full-page PNGs `desktop-<width>-light.png` / `-dark.png` into a printed folder (default `/tmp/ddv-shots-<timestamp>`). Per shot it prints the page height, whether there is horizontal overflow, and any JS console/page errors (exit status 2 on a JS error). Then open the PNGs with the Read tool (long pages: crop into slices first, e.g. with Pillow).

- Default is the real save (read-only). `--demo` renders a synthetic report with states the real save lacks (a completed Companion job, Villagers needing daily talk, an unknown Villager and Companion, long lists). `--report FILE.json` renders any report JSON.
- Desktop browser only (default 1100 px wide); `--width 800` checks a narrow half-screen window. There is no phone layout.
- For interactive checks (hover, click, resize, read DOM text) use the helper in `tools/pwpage.py`:

      import sys; sys.path.insert(0, "tools")
      from pwpage import app_page
      with app_page(width=800, scheme="dark", demo=True) as (page, errors):
          print(page.inner_text("#meta"), errors)

  Run it with `.venv/bin/python`.
- The `.venv` (about 680 MB, gitignored) can be recreated with: `python3 -m venv .venv; .venv/bin/pip install playwright; PLAYWRIGHT_BROWSERS_PATH=.venv/browsers .venv/bin/playwright install chromium`. The venv has no `cryptography`; the tool borrows the system copy.
