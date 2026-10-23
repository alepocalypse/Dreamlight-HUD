# Dreamlight HUD

A read-only companion for Disney Dreamlight Valley. It reads your own save file and shows
Villager jobs, Companion jobs, daily to-dos, event duties and more in a clean page or its own
window. It never writes to your game folder and sends nothing anywhere.

## What it shows

**Jobs and To-do.** Every Villager grouped by Profession, with the Profession's bonus chance. Below it,
the To-do list shows only the Villagers who still need attention (below max level with Daily talk or a
Favorite gift outstanding). Each card lists the gifts, with a check once you hold the item and where it
spawns. "Gather For Chests" counts raw materials toward 5 Large Chests, and Time-bending shows which
areas still have nodes.

![Jobs and To-do](docs/screenshots/jobs-and-todo.png)

**Event duties.** Star Path and Dreamlight/Mist duties in one task list. Duties that one action can
advance together are grouped into a single card, and the list is ordered so you can work top to bottom.
Use the checkboxes to hide a Star Path you are not playing.

![Event duties](docs/screenshots/event-duties.png)

**Companions by job.** Which Companions you have unlocked for each Job, which are equipped, and how far
each Critter has been fed. A green outline means every Companion for that Job is done.

![Companions by job](docs/screenshots/companions.png)

The page refreshes by itself every few seconds, so leave it open while you play.

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
