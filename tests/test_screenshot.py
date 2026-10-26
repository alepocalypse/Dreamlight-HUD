import importlib.util, os, sys, unittest

HERE = os.path.dirname(__file__)
TOOLS = os.path.join(HERE, "..", "tools")
sys.path.insert(0, TOOLS)
import pwpage, screenshot  # noqa: E402


class ShotPlan(unittest.TestCase):
    def test_default_is_light_and_dark_at_1100(self):
        self.assertEqual(screenshot.shot_plan(),
                         [("desktop-1100-light.png", 1100, "light"), ("desktop-1100-dark.png", 1100, "dark")])

    def test_scheme_and_width_narrow_it(self):
        self.assertEqual(screenshot.shot_plan("dark", 800), [("desktop-800-dark.png", 800, "dark")])

    def test_duty_mode_shots_are_named_for_it(self):
        self.assertEqual(screenshot.shot_plan("both", 400, duty=True),
                         [("duty-400-light.png", 400, "light"), ("duty-400-dark.png", 400, "dark")])


class VenvReexec(unittest.TestCase):
    def test_reexec_only_when_venv_exists_and_not_already_on_it(self):
        venv = os.path.join(HERE, "test_screenshot.py")  # any existing file stands in for the venv python
        self.assertEqual(pwpage.reexec_target("/usr/bin/python3", venv), venv)
        self.assertIsNone(pwpage.reexec_target(venv, venv))
        self.assertIsNone(pwpage.reexec_target("/usr/bin/python3", "/nonexistent/python"))


class DemoReport(unittest.TestCase):
    def test_exercises_states_the_real_save_lacks(self):
        r = screenshot.demo_report()
        self.assertEqual(r["status"], "ok")
        self.assertTrue(any(j["complete"] for j in r["companions"]["jobs"]))
        self.assertTrue(any(t["daily_talk_needed"] for t in r["todo"]))
        self.assertTrue(any(t["name"].startswith("Villager #") for t in r["todo"]))
        self.assertTrue(any(c["name"].startswith("Companion #") for c in r["companions"]["no_job"]))
        self.assertGreater(len(r["todo"]), 15)

    def test_duty_mode_shows_a_double_a_triple_and_a_quad(self):
        sizes = {a["size"] for a in screenshot.demo_report()["actions"]}
        self.assertLessEqual({"Double", "Triple", "Quad", "Single"}, sizes)

    def test_profession_cards_show_mixed_and_all_max_states(self):
        cards = screenshot.demo_report()["professions"]
        # a card with Villagers below max and some at max, and one where everyone is at max
        self.assertTrue(any(c["villagers"] and c["done"] for c in cards))
        self.assertTrue(any(not c["villagers"] and len(c["done"]) > 1 for c in cards))
        self.assertTrue(any(c["villagers"] and not c["done"] for c in cards))


@unittest.skipUnless(os.path.exists(pwpage.VENV_PYTHON) and importlib.util.find_spec("playwright"),
                     "needs the project venv with Playwright (run with .venv/bin/python)")
class BrowserRun(unittest.TestCase):
    def test_demo_renders_footer_without_errors(self):
        with pwpage.app_page(width=800, demo=True) as (page, errors):
            self.assertIn("Decode OK", page.inner_text("#meta"))
            self.assertEqual(errors, [])
            self.assertFalse(page.evaluate("document.documentElement.scrollWidth > window.innerWidth"))

    def test_duty_mode_renders_badged_cards_and_remembers_its_own_list_choice(self):
        with pwpage.app_page(width=400, demo=True, path="/duty") as (page, errors):
            self.assertEqual(page.eval_on_selector_all(".acard .badge", "els => els.map(e => e.textContent)"),
                             ["Quad", "Triple", "Double"])
            self.assertEqual(page.inner_text("#unclaimed"), "2 done, claim in game")
            self.assertIn("Haunting Elegance", page.inner_text("#actions"))
            page.get_by_label("Haunting Elegance").uncheck()
            self.assertNotIn("Haunting Elegance", page.inner_text("#actions"))
            self.assertEqual(page.evaluate("[localStorage.getItem('ddv-dutymode-off'), localStorage.getItem('ddv-duty-off')]"),
                             ['["Haunting Elegance"]', None])
            self.assertEqual(errors, [])
            self.assertFalse(page.evaluate("document.documentElement.scrollWidth > window.innerWidth"))


if __name__ == "__main__":
    unittest.main()
