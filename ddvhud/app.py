"""Locate the save, decode it read-only, build the report. Never writes."""
import datetime
import glob
import os
import sys

from .report import build_report
from .save import SaveDecodeError, load_profile

_GAME_DIR = os.path.join("AppData", "LocalLow", "Gameloft", "Disney Dreamlight Valley")


def default_root():
    """Save folder for this OS: the Windows user profile, or the Steam/Proton prefix on Linux."""
    if sys.platform == "win32":
        return os.path.join(os.path.expanduser("~"), _GAME_DIR)
    return os.path.join(os.path.expanduser(
        "~/.local/share/Steam/steamapps/compatdata/1401590/pfx/drive_c/users/steamuser"), _GAME_DIR)


DEFAULT_ROOT = default_root()


def find_save(root=DEFAULT_ROOT):
    """Return the newest steam_*/profile.json under root, or None."""
    hits = glob.glob(os.path.join(glob.escape(root), "steam_*", "profile.json"))
    return max(hits, key=os.path.getmtime) if hits else None


def report_for_save(path, now):
    report = build_report(load_profile(path), now)
    report["save_written"] = _iso_mtime(path)
    return report


def current_report(root_or_file, now):
    """Report for the save as it is now, or an error dict. Never returns stale data.

    Every call re-reads the save, so a rewrite by the game shows on the next poll.
    Errors carry "status" and "message" but no report data, so the page cannot show
    old numbers as if they were current.
    """
    path = root_or_file if os.path.isfile(root_or_file) else find_save(root_or_file)
    if path is None:
        return {"status": "save_not_found",
                "searched": root_or_file,
                "message": f"No save found under {root_or_file}. Choose your Dreamlight Valley "
                           "save folder (the one containing steam_*) or its profile.json, "
                           "or pass it with --save."}
    try:
        return {"status": "ok", **report_for_save(path, now)}
    except SaveDecodeError as e:
        return {"status": "decode_failed", "message": str(e), **_written(path)}
    except OSError as e:
        return {"status": "save_not_found", "message": f"Could not read {path}: {e}"}


def _written(path):
    try:
        return {"save_written": _iso_mtime(path)}
    except OSError:
        return {}


def _iso_mtime(path):
    return datetime.datetime.fromtimestamp(
        os.path.getmtime(path), datetime.timezone.utc).isoformat()
