import json, os, shutil, tempfile, threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

from ddvhud import config
from ddvhud.server import make_handler
from tests.test_read_only import PROFILE, encrypt


class PickSave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.save = os.path.join(self.tmp, "game", "steam_1_r")
        os.makedirs(self.save)
        with open(os.path.join(self.save, "profile.json"), "wb") as f:
            f.write(encrypt(PROFILE))
        self.cfg = os.path.join(self.tmp, "cfg", "config.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def serve(self, picker):
        empty = os.path.join(self.tmp, "empty")
        os.makedirs(empty, exist_ok=True)
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(empty, picker, self.cfg))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.shutdown)
        return f"http://127.0.0.1:{httpd.server_address[1]}"

    def get(self, base):
        return json.load(urllib.request.urlopen(base + "/report.json"))

    def post(self, base):
        return json.load(urllib.request.urlopen(urllib.request.Request(base + "/pick-save", method="POST")))

    def test_not_found_then_picked_and_remembered(self):
        base = self.serve(lambda: os.path.join(self.tmp, "game"))
        r = self.get(base)
        self.assertEqual(r["status"], "save_not_found")
        self.assertTrue(r["can_pick_save"])
        self.assertEqual(self.post(base), {"picked": True})
        self.assertEqual(self.get(base)["status"], "ok")
        self.assertEqual(config.load_save_path(self.cfg), os.path.join(self.tmp, "game"))

    def test_cancelled_dialog_changes_nothing(self):
        base = self.serve(lambda: None)
        self.assertEqual(self.post(base), {"picked": False})
        self.assertEqual(self.get(base)["status"], "save_not_found")
        self.assertIsNone(config.load_save_path(self.cfg))

    def test_no_picker_means_no_endpoint(self):
        base = self.serve(None)
        self.assertFalse(self.get(base)["can_pick_save"])
        with self.assertRaises(urllib.error.HTTPError):
            self.post(base)

    def test_unreadable_config_is_ignored(self):
        os.makedirs(os.path.dirname(self.cfg))
        with open(self.cfg, "w") as f:
            f.write("{nope")
        self.assertIsNone(config.load_save_path(self.cfg))
