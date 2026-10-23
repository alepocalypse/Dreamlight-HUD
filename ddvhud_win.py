"""PyInstaller entry point: the packaged app always opens the HUD in its own window."""
import sys

if "--window" not in sys.argv:
    sys.argv.append("--window")

import ddvhud.__main__  # noqa: E402,F401  (runs the CLI)
