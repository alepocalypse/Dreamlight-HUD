import threading, unittest, urllib.request
from datetime import datetime, timezone

from ddvhud.duty_mode import duty_actions
from ddvhud.report import build_report
from ddvhud.server import make_handler, window_spec
from http.server import ThreadingHTTPServer

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)


def task(state, cur=0, target=1):
    return {"Objective": {"CurAmount": cur, "TargetAmount": target}, "TaskState": "BattlePassTaskState_" + state}


def rotating(i, duty_id):   # a Dreamlight or Mist Duties slot, OnGoing at 0/5
    return {"SlotId": i, "DutyId": duty_id, "State": "DutySlotState_OnGoing",
            "StepData": {"ItemFilter": {"Data": None}, "TargetAmount": 5, "curAmount": 0}}


def duty(text, path="Seafaring", weekly=None, current=0, target=5, **extra):
    return {"path": path, "text": text, "current": current, "target": target, "weekly": weekly, **extra}


def group(label, *duties):   # do_together's shape: copies of the duties without the page's extra keys
    return {"label": label, "spans": len({d["path"] for d in duties}),
            "duties": [{k: d[k] for k in ("path", "text", "current", "target", "weekly")} for d in duties]}


def shown(actions):   # size, label, duty texts
    return [(a["size"], a["label"], [d["text"] for d in a["duties"]]) for a in actions]


class DutyActions(unittest.TestCase):
    def test_a_group_of_two_is_a_double_and_a_duty_in_no_group_a_single(self):
        a, b, c = duty("Catch any fish."), duty("Catch fish at Dazzle Beach."), duty("Mine for blue gems.")
        self.assertEqual(shown(duty_actions([a, b, c], [group("Catch fish at Dazzle Beach", a, b)])),
                         [("Double", "Catch fish at Dazzle Beach", ["Catch any fish.", "Catch fish at Dazzle Beach."]),
                          ("Single", "Mine for blue gems.", ["Mine for blue gems."])])

    def test_three_duties_make_a_triple_and_four_or_more_a_quad(self):
        ds = [duty(t) for t in "abcdefghijkl"]
        actions = duty_actions(ds, [group("Three", *ds[:3]), group("Four", *ds[3:7]), group("Five", *ds[7:12])])
        self.assertEqual([(a["label"], a["size"]) for a in actions], [("Five", "Quad"), ("Four", "Quad"), ("Three", "Triple")])

    def test_a_duty_in_two_actions_appears_under_both_and_not_as_a_single(self):
        any_fish, beach, seaweed = duty("any"), duty("beach"), duty("seaweed")
        actions = duty_actions([any_fish, beach, seaweed], [group("Beach", any_fish, beach), group("Seaweed", any_fish, seaweed)])
        self.assertEqual(shown(actions), [("Double", "Beach", ["any", "beach"]), ("Double", "Seaweed", ["any", "seaweed"])])

    def test_family_duties_are_not_merged_into_rows_cards(self):
        red = duty("Mine red gems.", family="Gems", row="Red", rank=1)
        blue = duty("Mine blue gems.", family="Gems", row="Blue", rank=1)
        fish_a, fish_b = duty("Catch 5 fish.", family="Fish", row="Any"), duty("Catch 20 fish.", weekly=1, family="Fish", row="Any")
        actions = duty_actions([red, fish_a, blue, fish_b], [group("Catch any fish", fish_a, fish_b)])
        self.assertEqual(shown(actions), [("Double", "Catch any fish", ["Catch 5 fish.", "Catch 20 fish."]),
                                          ("Single", "Mine red gems.", ["Mine red gems."]),
                                          ("Single", "Mine blue gems.", ["Mine blue gems."])])

    def test_action_duties_keep_the_helper_lines(self):
        a = duty("Catch fish at Dazzle Beach.", spot="Dazzle Beach: pier", zones=["Dazzle Beach"])
        b = duty("Catch any fish.")
        [action] = duty_actions([a, b], [group("Catch fish at Dazzle Beach", a, b)])
        self.assertEqual((action["duties"][0]["spot"], action["duties"][0]["zones"]), ("Dazzle Beach: pier", ["Dazzle Beach"]))

    def test_actions_rank_by_the_sum_of_their_duties_values_highest_first(self):
        a, b = duty("Catch any fish.", value=50), duty("Catch fish at Dazzle Beach.", value=100)
        gem, plant = duty("Mine for blue gems.", value=200), duty("Plant crops.", value=0)
        actions = duty_actions([a, b, gem, plant], [group("Catch fish at Dazzle Beach", a, b)])
        self.assertEqual([(a["label"], a["value"]) for a in actions],
                         [("Mine for blue gems.", 200), ("Catch fish at Dazzle Beach", 150), ("Plant crops.", 0)])

    def test_equal_values_rank_the_larger_action_first_then_keep_the_current_order(self):
        scrooge = [duty("Buy from Scrooge.", value=50), duty("Buy from Scrooge.", path="Haunting Elegance", value=50)]
        fish = [duty(f"Fish {n}.", value=25) for n in range(4)]
        later, earlier = duty("Pet a companion.", value=0), duty("Take a picture.", value=0)
        actions = duty_actions([*scrooge, *fish, later, earlier],
                               [group("Scrooge", *scrooge), group("Fish", *fish)])   # across two lists: first today
        self.assertEqual([(a["label"], a["value"]) for a in actions],
                         [("Fish", 100), ("Scrooge", 100), ("Pet a companion.", 0), ("Take a picture.", 0)])



class ReportActions(unittest.TestCase):
    def test_the_report_lists_actions_across_star_paths_and_singles_for_the_rest(self):
        progress = {"Seafaring2026": {"TasksProgress": [task("OnGoing", 1, 10)] + [task("NotStarted")] * 4
                                      + [task("OnGoing", 1, 3)]},
                    "HauntingElegance2026": {"TasksProgress": [task("NotStarted")] * 13 + [task("OnGoing", 2, 4)]}}
        actions = build_report({"Player": {"BattlePassStates": {"Progress": progress}}}, NOW)["actions"]
        self.assertEqual([(a["size"], [(d["path"], d["text"]) for d in a["duties"]]) for a in actions], [
            ("Double", [("Seafaring Star Path", "Buy something from Scrooge McDuck's Store."),
                        ("Haunting Elegance", "Buy something from Scrooge McDuck's Store.")]),
            ("Single", [("Seafaring Star Path", "Catch any fish.")])])

    def test_no_duties_no_actions(self):
        self.assertEqual(build_report({}, NOW)["actions"], [])

    def test_rotating_duties_carry_the_reward_their_set_pays_and_unknown_ids_none(self):
        def slot(i, duty_id):
            return {"SlotId": i, "DutyId": duty_id, "State": "DutySlotState_OnGoing",
                    "StepData": {"ItemFilter": {"Data": None}, "TargetAmount": 5, "curAmount": 0}}
        profile = {"Player": {"DutySlots": {"1540000000": {"Slots": [slot(0, 2110000034)]},
                                            "1540000101": {"Slots": [slot(0, 2110000040), slot(1, 7)]}}}}
        duties = {d["text"]: d.get("reward") for a in build_report(profile, NOW)["actions"] for d in a["duties"]}
        self.assertEqual(duties, {"Plant 5 Vegetables": {"amount": 150, "currency": "Dreamlight"},
                                  "Catch 5 Fish": {"amount": 250, "currency": "Mist"},
                                  "Duty #7": None})

    def test_star_path_duties_carry_their_token_reward_and_duties_missing_from_the_table_none(self):
        progress = {"HauntingElegance2026": {"TasksProgress": [task("OnGoing", 1, 3)] + [task("NotStarted")] * 130
                                             + [task("OnGoing", 0, 1)],
                                             "WeeklyTasksProgress": [{"TasksProgress": [task("OnGoing", 0, 30)]}]}}
        duties = {d["text"]: d.get("reward") for a in build_report({"Player": {"BattlePassStates": {"Progress": progress}}},
                                                                   NOW)["actions"] for d in a["duties"]}
        self.assertEqual(duties, {"Uproot Night Thorns.": {"amount": 5, "currency": "Pumpkin Tokens"},
                                  "Mine 20 orange gems.": {"amount": 30, "currency": "Pumpkin Tokens"},
                                  "Duty #132": None})

    def test_a_star_path_token_is_worth_ten_dreamlight(self):
        progress = {"HauntingElegance2026": {"TasksProgress": [task("OnGoing", 1, 3)]}}
        [action] = build_report({"Player": {"BattlePassStates": {"Progress": progress}}}, NOW)["actions"]
        self.assertEqual((action["duties"][0]["reward"]["amount"], action["duties"][0]["value"], action["value"]), (5, 50, 50))

    def test_dreamlight_and_mist_count_at_par_and_an_unknown_rotating_duty_zero(self):
        profile = {"Player": {"DutySlots": {"1540000000": {"Slots": [rotating(0, 2110000034)]},
                                            "1540000101": {"Slots": [rotating(0, 2110000040), rotating(1, 7)]}}}}
        actions = build_report(profile, NOW)["actions"]
        self.assertEqual([(a["label"], a["value"]) for a in actions],
                         [("Catch 5 Fish", 250), ("Plant 5 Vegetables", 150), ("Duty #7", 0)])

    def test_a_star_path_duty_missing_from_the_table_ranks_at_its_paths_median_reward_and_shows_none(self):
        # Seafaring's known Rewards: 5 x3, 10 x9, 15 x10, 20 x5, 25 x1; the 14th and 15th are both 15 tokens
        progress = {"Seafaring2026": {"TasksProgress": [task("NotStarted")] * 25 + [task("OnGoing", 0, 1)],
                                      "WeeklyTasksProgress": [{}, {"TasksProgress": [task("OnGoing", 0, 1)]}]}}
        actions = build_report({"Player": {"BattlePassStates": {"Progress": progress}}}, NOW)["actions"]
        self.assertEqual([(a["label"], a["value"], a["duties"][0].get("reward")) for a in actions],
                         [("Duty #26", 150, None), ("Hang out with a mermaid princess.", 150, None)])

    def test_a_star_path_with_no_known_rewards_ranks_its_duties_zero(self):
        progress = {"NewPath2027": {"TasksProgress": [task("OnGoing", 0, 1)]}}
        [action] = build_report({"Player": {"BattlePassStates": {"Progress": progress}}}, NOW)["actions"]
        self.assertEqual(action["value"], 0)



class DutyPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("/nonexistent"))
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        r = urllib.request.urlopen(f"http://127.0.0.1:{self.httpd.server_address[1]}{path}")
        return r.headers["Content-Type"], r.read().decode()

    def test_duty_mode_has_its_own_url_linking_back_to_the_full_hud(self):
        ctype, body = self.get("/duty")
        self.assertEqual(ctype, "text/html; charset=utf-8")
        self.assertIn("<title>Duty mode</title>", body)
        self.assertIn('href="/"', body)

    def test_the_full_hud_links_to_duty_mode(self):
        self.assertIn('href="/duty"', self.get("/")[1])



class WindowMode(unittest.TestCase):
    def test_duty_opens_a_narrow_window_straight_into_duty_mode(self):
        self.assertEqual(window_spec(5000, duty=True), ("http://127.0.0.1:5000/duty", 400, 900))

    def test_default_window_is_the_full_hud(self):
        self.assertEqual(window_spec(5000), ("http://127.0.0.1:5000/", 1100, 900))


if __name__ == "__main__":
    unittest.main()
