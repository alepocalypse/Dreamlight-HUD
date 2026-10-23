"""The one file this app writes: the save location the user picked. Never touches the game folder."""
import json
import os
import sys


def config_path():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return os.path.join(base, "DreamlightHUD", "config.json")
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "ddvhud", "config.json")


def load_save_path(path=None):
    """The remembered save folder or profile.json, or None if unset or unreadable."""
    try:
        with open(path or config_path(), encoding="utf-8") as f:
            value = json.load(f).get("save")
    except (OSError, ValueError, AttributeError):
        return None
    return value if isinstance(value, str) and value else None


def store_save_path(save, path=None):
    path = path or config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"save": save}, f)
