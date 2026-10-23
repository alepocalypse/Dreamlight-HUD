# Dreamlight HUD

A read-only companion for Disney Dreamlight Valley. It reads your own save file and shows
Villager jobs, Companion jobs, daily to-dos, event duties and more in a clean page or its own
window. It never writes to your game folder and sends nothing anywhere.

## Windows

Download `DreamlightHUD.exe` from the [latest release](../../releases/latest) and run it.
Windows SmartScreen may warn about an unsigned app: click **More info**, then **Run anyway**.
If your save is not found, use **Choose save folder…** and pick the folder that contains
`steam_*`. The default is `%USERPROFILE%\AppData\LocalLow\Gameloft\Disney Dreamlight Valley`.

## From source

    pip install cryptography            # plus pywebview for the window mode
    python3 -m ddvhud --window          # own window
    python3 -m ddvhud --port 8765       # browser at http://127.0.0.1:8765/
    python3 -m ddvhud --save PATH       # save folder or profile.json

Tests: `python3 -m unittest discover -s tests`

## Legal

Unofficial, fan-made, and not affiliated with Disney or Gameloft. Code is MIT licensed
(see `LICENSE`). Character portraits and icons under `ddvhud/static/` are Disney/Gameloft
artwork, are not covered by that license, and are included only to identify game content.
Disney Dreamlight Valley and its characters are trademarks and copyrights of Disney and
Gameloft. Recipe and item data comes from the community
[Dreamlight Valley Wiki](https://dreamlightvalleywiki.com/).
