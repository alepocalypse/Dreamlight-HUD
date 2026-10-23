import threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

from ddvhud.server import make_handler

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PROFESSIONS = ["digging", "fishing", "foraging", "gardening", "mining", "timebending",
               "flowers", "wood", "snippets"]


class RoleIcons(unittest.TestCase):
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

    def test_each_role_icon_is_served_as_png(self):
        for name in PROFESSIONS:
            status, headers, body = self.get(f"/roles/{name}.png")
            self.assertEqual(status, 200, name)
            self.assertEqual(headers["Content-Type"], "image/png")
            self.assertTrue(body.startswith(PNG_MAGIC), name)
            self.assertIn("max-age", headers["Cache-Control"])

    def test_daily_talk_icon_is_served_as_png(self):
        status, headers, body = self.get("/roles/talk.png")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "image/png")
        self.assertTrue(body.startswith(PNG_MAGIC))

    def test_paths_outside_the_icon_folder_are_refused(self):
        for path in ["/roles/..%2fserver.py", "/roles/../server.py", "/roles/%2e%2e/server.py",
                     "/roles/..%2f..%2fstatic%2findex.html", "/roles/sub%2fdigging.png",
                     "/roles/digging.png/../../server.py", "/roles/%2fetc%2fpasswd",
                     "/roles/..\\server.py", "/roles/digging.png%00.txt"]:
            status, _, body = self.get(path)
            self.assertEqual(status, 404, path)
            self.assertNotIn(b"make_handler", body)

    def test_non_png_and_missing_files_are_refused(self):
        for path in ["/roles/SOURCES.txt", "/roles/nothing.png", "/roles/", "/roles/digging"]:
            self.assertEqual(self.get(path)[0], 404, path)


if __name__ == "__main__":
    unittest.main()
