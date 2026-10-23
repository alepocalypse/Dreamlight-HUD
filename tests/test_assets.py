import threading, unittest, urllib.error, urllib.request
from http.server import ThreadingHTTPServer

from ddvhud.server import make_handler


class StaticAssets(unittest.TestCase):
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

    def test_portrait_traversal_attempts_are_refused(self):
        for path in ["/portraits/../report.json", "/portraits/%2e%2e/x.png",
                     "/portraits/..%2freport.json", "/portraits/1%2f..%2f2.png",
                     "/portraits/%2e%2e%2f%2e%2e%2fstatic%2findex.html"]:
            status, _, body = self.get(path)
            self.assertEqual(status, 404, path)
            self.assertEqual(body, b"not found", path)

    def test_role_traversal_and_encoded_slashes_get_the_plain_404(self):
        for path in ["/roles/../report.json", "/roles/%2e%2e/x.png", "/roles/%2E%2E%2Fdigging.png",
                     "/roles/a%2fdigging.png", "/roles/%252e%252e/digging.png"]:
            status, _, body = self.get(path)
            self.assertEqual(status, 404, path)
            self.assertEqual(body, b"not found", path)

    def test_wrong_extension_is_refused(self):
        for path in ["/roles/digging.jpg", "/roles/digging.png.txt", "/roles/digging.png/",
                     "/portraits/10000002.jpg", "/portraits/10000002", "/portraits/10000002.png.bak"]:
            self.assertEqual(self.get(path)[0], 404, path)

    def test_names_the_pattern_does_not_allow_are_refused(self):
        for path in ["/roles/Digging.png", "/roles/DIGGING.PNG", "/roles/digging.PNG",
                     "/roles/dig-ging.png", "/roles/dig%20ging.png", "/roles/10000002.png",
                     "/portraits/abc.png", "/portraits/+10000002.png", "/portraits/-1.png",
                     "/portraits/10000002.PNG", "/portraits/%2010000002.png", "/portraits/.png"]:
            self.assertEqual(self.get(path)[0], 404, path)

    def test_query_string_is_ignored(self):
        for path in ["/roles/digging.png?v=2", "/portraits/10000002.png?x=/../..", "/roles/digging.png?"]:
            status, headers, body = self.get(path)
            self.assertEqual(status, 200, path)
            self.assertEqual(headers["Content-Type"], "image/png")
            self.assertTrue(body.startswith(b"\x89PNG"), path)
        self.assertEqual(self.get("/roles/nothing.png?digging.png")[0], 404)

    def test_unknown_prefix_is_404(self):
        for path in ["/other/digging.png", "/role/digging.png", "/roles", "/portraits", "/static/roles/digging.png",
                     "/ROLES/digging.png"]:
            status, _, body = self.get(path)
            self.assertEqual(status, 404, path)
            self.assertEqual(body, b"not found", path)

    def test_both_prefixes_send_the_same_headers(self):
        _, a, _ = self.get("/roles/digging.png")
        _, b, _ = self.get("/portraits/10000002.png")
        for h in ("Content-Type", "Cache-Control"):
            self.assertEqual(a[h], b[h])
        self.assertEqual(a["Content-Type"], "image/png")
        self.assertEqual(a["Cache-Control"], "max-age=86400")

    def test_misses_on_both_prefixes_look_alike(self):
        _, a, abody = self.get("/roles/nothing.png")
        _, b, bbody = self.get("/portraits/99999999999.png")
        self.assertEqual(abody, bbody)
        self.assertEqual(a["Content-Type"], "text/plain")
        self.assertEqual(b["Content-Type"], "text/plain")
        self.assertEqual(a["Cache-Control"], "no-store")
        self.assertEqual(b["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
