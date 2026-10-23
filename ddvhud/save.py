"""Read-only decoder for Disney Dreamlight Valley profile.json (AES-256-ECB -> zip -> JSON)."""
import io
import json
import zipfile

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

# Key per https://reversing.falkrian.com/posts/a-closer-look-at-disney-dreamlight-valleys-save-encryption/
# (game 1.24.13.33). May change in a patch.
KEY = b"b5qhh8saJ8UlDJUzTZXd2Tg6mbo8W8n5"


class SaveDecodeError(Exception):
    pass


def load_profile(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
        padded = dec.update(raw) + dec.finalize()
        unpadder = PKCS7(128).unpadder()
        data = unpadder.update(padded) + unpadder.finalize()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return json.loads(z.read("profile"))
    except Exception as e:
        raise SaveDecodeError(
            f"Could not decode {path}: the game's key may have changed in a patch ({e})"
        ) from e
