#!/usr/bin/env python3
"""Screenshot the HUD page (Playwright + Chromium), for agents and humans.

    python3 tools/screenshot.py [--demo | --report FILE.json] [--width N]
                                   [--scheme light|dark|both] [--out DIR]

Re-runs itself under the project venv (.venv/bin/python) when it exists. Starts its own
app server on a free port, never the user's; read-only toward the game's folders.
Full-page PNGs; prints per shot the path, size, horizontal overflow and JS errors.
Exit status 2 if any page raised a JS error. See "Seeing the page" in CLAUDE.md.
"""
import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pwpage  # noqa: E402
from ddvhud.report import build_report  # noqa: E402

DEFAULT_WIDTH = 1100  # desktop browser only: there is no phone layout to check


def shot_plan(scheme="both", width=DEFAULT_WIDTH):
    """[(file name, width, scheme)] for the requested colour scheme(s)."""
    schemes = ["light", "dark"] if scheme == "both" else [scheme]
    return [(f"desktop-{width}-{s}.png", width, s) for s in schemes]


def demo_report():
    """Synthetic report built through the real build_report from an invented profile."""
    from ddvhud.items import ITEMS
    from ddvhud.villagers import PROFESSIONS, VILLAGERS
    ids = sorted(VILLAGERS)
    profs = sorted(PROFESSIONS)
    gifts = sorted(ITEMS)

    def char(i, cid, status, level, prof, talked, nslots):
        return {"Base": {"id": cid}, "Status": "CharacterStatus_" + status,
                "FriendshipLevel": level, "ProfessionID": prof,
                "DiscussedWithTheAvatarToday": talked,
                "LastGiftDate": "2026-10-19T08:00:00Z",
                "PreferredItemSlots": [{"PreferredItemId": gifts[(i * 3 + s) % len(gifts)],
                                        "Gifted": s == 0 and i % 2 == 0} for s in range(nslots)]}

    chars = []
    for i, cid in enumerate(ids[:40]):
        # levels 0..10 spread over the Professions; the third Profession (Mining) is all at max,
        # the fourth (Foraging) has nobody at max
        level = 10 if i % 6 == 2 else (i * 3) % 11
        if i % 6 == 3 and level == 10:
            level = 9
        chars.append(char(i, cid, "InVillage", level, profs[i % len(profs)], i % 3 == 0, 3))
    chars.append(char(90, 10000999, "InVillage", 4, 0, False, 3))            # unknown name
    chars.append(char(91, 10000998, "InVillage", 6, 1500000999, False, 0))  # unknown profession
    for i, cid in enumerate(ids[40:50]):
        chars.append(char(i, cid, "InRealm", 2, 0, False, 0))
    for i, cid in enumerate(ids[50:]):
        chars.append(char(i, cid, "Secret", 0, 0, False, 0))
    # chests holding about every other gift item (counts 1..), plus decoys that must not count
    chest_items = [{"ItemID": g, "Amount": 1 + (n % 9) * 6, "State": None}
                   for n, g in enumerate(gifts) if n % 2 == 0]
    containers = {"0": {"ID": 0, "BelongsToPlayer": True, "ParentItemID": None,
                        "Inventory": [{"ItemID": g, "Amount": 1 + n % 4, "State": None}
                                      for n, g in enumerate(gifts) if n % 4 in (0, 1)]},
                  "1": {"ID": 1, "BelongsToPlayer": True, "ParentItemID": None,
                        "Inventory": [{"ItemID": g, "Amount": 5, "State": None} for g in gifts[1::3]]},
                  "2": {"ID": 2, "BelongsToPlayer": False, "ParentItemID": 40001028,
                        "Inventory": [{"ItemID": g, "Amount": 5, "State": None} for g in gifts[2::3]]},
                  "3": {"ID": 3, "BelongsToPlayer": True, "ParentItemID": 40001190,
                        "Inventory": chest_items[: len(chest_items) // 2]},
                  "4": {"ID": 4, "BelongsToPlayer": True, "ParentItemID": 40000229,
                        "Inventory": chest_items[len(chest_items) // 2:]
                        + [{"ItemID": 31700002, "Amount": 90, "State": None},    # Dark Wood: 35 short
                           {"ItemID": 31700007, "Amount": 5, "State": None}]}}   # Gold Ingot: 20 short
    now = datetime.datetime.now(datetime.timezone.utc)

    def duty(state, cur, target):
        return {"Objective": {"CurAmount": cur, "TargetAmount": target}, "TaskState": "BattlePassTaskState_" + state}

    profile = {
        "LastDailyReset": "2026-10-19T05:00:00Z",
        "World": {"Characters": chars,
                  "GridCollection": {"Grids": {"1": {"Objects": {   # 40 loose Dark Wood in the world
                      str(n): {"ID": n, "ItemID": 31700002} for n in range(40)}}}},
                  "Critters": [{"CritterItemID": 120100000, "NumberOfFeedingDone": 1},
                               {"CritterItemID": 120100002, "NumberOfFeedingDone": 2},
                               {"CritterItemID": 120100003, "NumberOfFeedingDone": 0},
                               {"CritterItemID": 120100004, "NumberOfFeedingDone": 3},
                               {"CritterItemID": 129999999, "NumberOfFeedingDone": 1}]},
        "Player": {
            "BattlePassStates": {"Progress": {   # a Star Path with a done duty, a claimed one and a weekly set
                "Seafaring2026": {
                    "CurrencyAmount": 35,
                    "EndDate": (now + datetime.timedelta(days=12, hours=3)).isoformat(),
                    "TasksProgress": [duty("OnGoing", 2, 10), duty("Completed", 15, 15), duty("CurrencyClaimed", 1, 1),
                                      duty("NotStarted", 0, 5), duty("OnGoing", 14, 15)],
                    "WeeklyTasksProgress": [{"TasksProgress": [duty("CurrencyClaimed", 20, 20)]},
                                            {"TasksProgress": [duty("OnGoing", 3, 20), duty("Completed", 5, 5)]}]}}},
            "ContainerInventories": containers,
            "AssignedPets": [120000013, 120000001, 120000099],
            "Pets": [{"PetItemID": 120000002, "FriendshipLevel": 5},
                     {"PetItemID": 120000013, "FriendshipLevel": 5},
                     {"PetItemID": 120000001, "FriendshipLevel": 3},
                     {"PetItemID": 120000005, "FriendshipLevel": 1},
                     {"PetItemID": 120000017, "FriendshipLevel": 2},
                     {"PetItemID": 129999990, "FriendshipLevel": 1}]},
    }
    report = {"status": "ok", **build_report(profile, now)}
    report["save_written"] = now.isoformat()
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description="PNG screenshots of the HUD page (Playwright/Chromium)")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--report", metavar="FILE.json", help="render this report JSON instead of the real save")
    src.add_argument("--demo", action="store_true", help="render a built-in synthetic report")
    p.add_argument("--width", type=int, default=DEFAULT_WIDTH,
                   help="viewport width in px (default 1100; e.g. 800 for a half-screen window)")
    p.add_argument("--scheme", choices=["light", "dark", "both"], default="both")
    p.add_argument("--out", help="output folder (default /tmp/ddv-shots-<timestamp>)")
    p.add_argument("--save", default=pwpage.app.DEFAULT_ROOT, help="save folder or profile.json (real-save mode)")
    a = p.parse_args(argv)

    target = pwpage.reexec_target(sys.executable)
    if target and not os.environ.get("DDV_SCREENSHOT_REEXEC"):
        os.environ["DDV_SCREENSHOT_REEXEC"] = "1"
        os.execv(target, [target, os.path.abspath(__file__)] + (argv if argv is not None else sys.argv[1:]))

    import json
    report = None
    if a.report:
        with open(a.report, encoding="utf-8") as f:
            report = json.load(f)
    out = os.path.abspath(a.out or "/tmp/ddv-shots-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out, exist_ok=True)
    js_errors = False
    try:
        for name, width, scheme in shot_plan(a.scheme, a.width):
            with pwpage.app_page(width=width, scheme=scheme, report=report, demo=a.demo, save=a.save) as (page, errs):
                path = os.path.join(out, name)
                page.screenshot(path=path, full_page=True)
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                height = page.evaluate("document.documentElement.scrollHeight")
                print(f"{path}  {width}x{height}  horizontal-overflow={'YES' if overflow else 'no'}  "
                      f"js-errors={len(errs)}")
                for e in errs:
                    print(f"    JS ERROR: {e}")
                js_errors = js_errors or bool(errs)
    except pwpage.SetupError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"Screenshots in {out}")
    return 2 if js_errors else 0


if __name__ == "__main__":
    sys.exit(main())
