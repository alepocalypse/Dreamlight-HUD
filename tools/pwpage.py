"""Reusable Playwright helper: a ready page for the HUD app, for screenshots and checks.

Run under the project venv: .venv/bin/python (see "Seeing the page" in CLAUDE.md).

    from pwpage import app_page            # with tools/ on sys.path
    with app_page(width=390, scheme="dark", demo=True) as (page, errors):
        page.hover("#todolist .vcard")
        print(page.inner_text("#meta"), errors)

Starts its own app server on a free port (never the user's), reads the save only through
the app's own read-only code, stops the server on exit. Standard library + Playwright.
"""
import contextlib
import json
import os
import sys
import threading
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = os.path.join(ROOT, ".venv", "bin", "python")
BROWSERS = os.path.join(ROOT, ".venv", "browsers")
sys.path.insert(0, ROOT)


def _borrow_system_cryptography():
    """The venv has no 'cryptography' (the app's only dependency); borrow the system copy
    (same Python version) by appending its site-packages as a last-resort path entry."""
    try:
        import cryptography  # noqa: F401
        return
    except ImportError:
        pass
    import subprocess
    r = subprocess.run(["/usr/bin/python3", "-c",
                        "import cryptography,os;print(os.path.dirname(os.path.dirname(cryptography.__file__)))"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        sys.path.append(r.stdout.strip())


_borrow_system_cryptography()

from ddvhud import app, server  # noqa: E402


class SetupError(Exception):
    pass


def reexec_target(executable, venv_python=VENV_PYTHON):
    """The venv interpreter to re-run under, or None if already on it / it does not exist."""
    if not os.path.exists(venv_python):
        return None
    if os.path.abspath(executable) == os.path.abspath(venv_python):
        return None
    return venv_python


def load_playwright():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", BROWSERS)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SetupError(
            "Playwright is not installed for this Python. Recreate the project venv:\n"
            "  python3 -m venv .venv && .venv/bin/pip install playwright\n"
            "  PLAYWRIGHT_BROWSERS_PATH=.venv/browsers .venv/bin/playwright install chromium\n"
            "and run with .venv/bin/python.")
    return sync_playwright


@contextlib.contextmanager
def app_page(width=1100, height=900, scheme="light", report=None, demo=False, save=app.DEFAULT_ROOT):
    """Yield (page, errors) with the app loaded and rendered.

    report: a report dict served as /report.json instead of the real save.
    demo: use the synthetic demo report (tools/screenshot.py demo_report).
    errors: list that collects JS page errors and console errors.
    """
    sync_playwright = load_playwright()
    if demo:
        from screenshot import demo_report
        report = demo_report()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(save))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as e:
                raise SetupError(f"Could not start Chromium ({e}). Is PLAYWRIGHT_BROWSERS_PATH "
                                 f"{os.environ['PLAYWRIGHT_BROWSERS_PATH']} populated?") from e
            try:
                ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
                page = ctx.new_page()
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))

                def console(m):
                    # a missing portrait file is by design (the page shows a placeholder block
                    # for it, e.g. the demo's "Villager #id"), so its 404 is not an error
                    url = (m.location or {}).get("url", "")
                    if m.type == "error" and not ("/portraits/" in url and "404" in m.text):
                        errors.append(m.text)
                page.on("console", console)
                if report is not None:
                    body = json.dumps(report)
                    page.route("**/report.json", lambda r: r.fulfill(
                        status=200, content_type="application/json", body=body))
                page.goto(f"http://127.0.0.1:{httpd.server_address[1]}/")
                page.wait_for_function(
                    "document.getElementById('meta').textContent.includes('Decode OK')"
                    " || document.getElementById('err').style.display === 'block'", timeout=15000)
                page.wait_for_load_state("networkidle")
                yield page, errors
            finally:
                browser.close()
    finally:
        httpd.shutdown()
