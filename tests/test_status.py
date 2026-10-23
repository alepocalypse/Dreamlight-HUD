import os, shutil, tempfile, unittest
from datetime import datetime, timezone

from ddvhud.app import current_report
from tests.test_report import NOW
from tests.test_read_only import PROFILE, encrypt


class CurrentReport(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        folder = os.path.join(self.root, "steam_1_r")
        os.makedirs(folder)
        self.path = os.path.join(folder, "profile.json")
        self.write(PROFILE)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, profile, mtime=None):
        with open(self.path, "wb") as f:
            f.write(encrypt(profile))
        if mtime:
            os.utime(self.path, (mtime, mtime))

    def test_ok_has_status_and_last_written(self):
        self.write(PROFILE, mtime=1_700_000_000)
        r = current_report(self.root, NOW)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["save_written"], "2023-11-14T22:13:20+00:00")
        self.assertEqual(r["summary"]["max_level"], 1)

    def test_rewritten_save_is_picked_up_without_restart(self):
        self.assertEqual(current_report(self.root, NOW)["summary"]["max_level"], 1)
        self.write({"World": {"Characters": []}})
        self.assertEqual(current_report(self.root, NOW)["summary"]["max_level"], 0)

    def test_save_option_accepts_a_profile_file(self):
        self.assertEqual(current_report(self.path, NOW)["status"], "ok")

    def test_undecodable_save_is_error_without_data(self):
        with open(self.path, "wb") as f:
            f.write(b"x" * 64)
        r = current_report(self.root, NOW)
        self.assertEqual(r["status"], "decode_failed")
        self.assertIn("key may have changed", r["message"])
        self.assertIn("save_written", r)
        self.assertNotIn("summary", r)
        self.assertNotIn("villagers", r)

    def test_missing_folder_is_clear_error(self):
        missing = os.path.join(self.root, "nope")
        r = current_report(missing, NOW)
        self.assertEqual(r["status"], "save_not_found")
        self.assertIn(missing, r["message"])
        self.assertIn("--save", r["message"])
        self.assertNotIn("summary", r)

    def test_save_removed_after_start_is_not_found(self):
        os.remove(self.path)
        self.assertEqual(current_report(self.root, NOW)["status"], "save_not_found")


if __name__ == "__main__":
    unittest.main()
