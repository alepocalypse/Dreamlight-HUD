import os, threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

from ddvhud.server import make_handler
from ddvhud.villagers import VILLAGERS

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PORTRAITS = os.path.join(os.path.dirname(__file__), "..", "ddvhud", "static", "portraits")
# Roster Villagers intentionally without a portrait file (the page shows a placeholder).
NO_PORTRAIT = set()


class Portraits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("/nonexistent"))
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}")
            return r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read()

    def test_a_portrait_is_served_as_png(self):
        status, headers, body = self.get("/portraits/10000003.png")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "image/png")
        self.assertTrue(body.startswith(PNG_MAGIC))
        self.assertIn("max-age", headers["Cache-Control"])

    def test_paths_outside_the_folder_are_refused(self):
        for path in ["/portraits/..%2fserver.py", "/portraits/../server.py", "/portraits/%2e%2e/server.py",
                     "/portraits/..%2f..%2fstatic%2findex.html", "/portraits/sub%2f10000003.png",
                     "/portraits/10000003.png/../../server.py", "/portraits/%2fetc%2fpasswd",
                     "/portraits/..\\server.py", "/portraits/10000003.png%00.txt",
                     "/portraits/../roles/digging.png", "/portraits/..%2froles%2fdigging.png"]:
            status, _, body = self.get(path)
            self.assertEqual(status, 404, path)
            self.assertNotIn(b"make_handler", body)

    def test_non_png_and_missing_files_are_refused(self):
        for path in ["/portraits/SOURCES.txt", "/portraits/1.png", "/portraits/", "/portraits/10000003",
                     "/portraits/abc.png"]:
            self.assertEqual(self.get(path)[0], 404, path)

    def test_every_roster_villager_has_a_portrait_file(self):
        missing = {vid for vid in VILLAGERS if not os.path.isfile(os.path.join(PORTRAITS, f"{vid}.png"))}
        self.assertEqual(missing, NO_PORTRAIT)


if __name__ == "__main__":
    unittest.main()
