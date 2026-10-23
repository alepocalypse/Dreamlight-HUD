import builtins, io, json, os, shutil, stat, tempfile, unittest, zipfile
from datetime import datetime, timezone
from unittest import mock

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from ddvhud import save
from ddvhud.app import find_save, report_for_save

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
PROFILE = {"World": {"Characters": [
    {"Base": {"id": 10000003}, "Status": "CharacterStatus_InVillage",
     "FriendshipLevel": 10, "ProfessionID": 0}]}}


def encrypt(profile):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("profile", json.dumps(profile))
    padder = PKCS7(128).padder()
    data = padder.update(buf.getvalue()) + padder.finalize()
    enc = Cipher(algorithms.AES(save.KEY), modes.ECB()).encryptor()
    return enc.update(data) + enc.finalize()


class GameFolderIsNeverModified(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        folder = os.path.join(self.root, "Gameloft", "Disney Dreamlight Valley", "steam_123_r")
        os.makedirs(folder)
        self.path = os.path.join(folder, "profile.json")
        with open(self.path, "wb") as f:
            f.write(encrypt(PROFILE))
        os.chmod(self.path, 0o444)
        for d, _, _ in os.walk(self.root):
            os.chmod(d, 0o555)

    def tearDown(self):
        for d, _, _ in os.walk(self.root):
            os.chmod(d, 0o755)
        os.chmod(self.path, 0o666)  # Windows cannot delete a read-only file
        shutil.rmtree(self.root)

    def snapshot(self):
        return [(p, os.stat(p).st_mtime_ns, os.stat(p).st_size)
                for d, _, fs in os.walk(self.root) for p in [d] + [os.path.join(d, f) for f in fs]]

    def test_find_and_read_save_without_modifying_anything(self):
        before = self.snapshot()
        real_open = builtins.open

        def guarded_open(file, mode="r", *a, **k):
            if any(ch in mode for ch in "wax+"):
                raise AssertionError(f"open for writing: {file!r} {mode!r}")
            return real_open(file, mode, *a, **k)

        def forbidden(name):
            def f(*a, **k):
                raise AssertionError(f"{name} called")
            return f

        with mock.patch("builtins.open", guarded_open), \
             mock.patch("os.rename", forbidden("rename")), \
             mock.patch("os.replace", forbidden("replace")), \
             mock.patch("os.remove", forbidden("remove")), \
             mock.patch("os.unlink", forbidden("unlink")), \
             mock.patch("os.rmdir", forbidden("rmdir")), \
             mock.patch("os.mkdir", forbidden("mkdir")), \
             mock.patch("os.makedirs", forbidden("makedirs")), \
             mock.patch("shutil.rmtree", forbidden("rmtree")):
            found = find_save(os.path.join(self.root, "Gameloft", "Disney Dreamlight Valley"))
            self.assertEqual(found, self.path)
            report = report_for_save(found, NOW)
        self.assertEqual(report["summary"]["max_level"], 1)
        self.assertEqual(self.snapshot(), before)

    def test_find_save_missing_folder_returns_none(self):
        self.assertIsNone(find_save(os.path.join(self.root, "nope")))


if __name__ == "__main__":
    unittest.main()
