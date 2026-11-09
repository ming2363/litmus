import gzip
import io
import os
import stat
import tarfile
import tempfile
import time
import unittest
from pathlib import Path

from litmus.crypto import (
    CryptoError,
    decrypt,
    encrypt,
    pack_dir,
    seal_dir,
    unpack_bytes,
    unseal_to,
)


def _make_tar_gz_bytes(builder) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tf:
            builder(tf)
    return buf.getvalue()


class TestCrypto(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip_and_tamper_detection(self):
        for payload in (b"", b"hello litmus", os.urandom(1024 * 64 + 13)):
            blob1 = encrypt(payload)
            blob2 = encrypt(payload)
            self.assertTrue(blob1.startswith(b"LITMUS1"))
            # 每次加密使用随机 nonce，密文应不同
            self.assertNotEqual(blob1, blob2)
            self.assertEqual(decrypt(blob1), payload)
            self.assertEqual(decrypt(blob2), payload)

        sample = encrypt(b"secret-answer")
        # 篡改 header / nonce / 密文 / tag 均应失败
        for idx in (0, 8, 23, len(sample) - 1):
            tampered = bytearray(sample)
            tampered[idx] ^= 0x01
            with self.assertRaises(CryptoError):
                decrypt(bytes(tampered))

        with self.assertRaises(CryptoError):
            decrypt(b"LITMUS1short")

    def test_pack_dir_reproducible_and_seal_unseal_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            (src / "sub").mkdir(parents=True)
            (src / "b.txt").write_bytes(("beta\n").encode("utf-8"))
            (src / "sub" / "run.sh").write_bytes(("#!/bin/sh\necho ok\n").encode("utf-8"))
            os.chmod(src / "sub" / "run.sh", 0o755)
            (src / "a.txt").write_bytes(("alpha\n").encode("utf-8"))

            packed1 = pack_dir(src)
            time.sleep(0.05)
            # 修改 mtime 后重新打包，输出字节流仍应完全一致
            os.utime(src / "a.txt", (1700000000, 1700000000))
            packed2 = pack_dir(src)
            self.assertEqual(packed1, packed2)

            enc_file = root / "test.grade.enc"
            seal_dir(src, enc_file)
            dest = root / "dest"
            unseal_to(enc_file, dest)

            self.assertEqual((dest / "a.txt").read_text(encoding="utf-8"), "alpha\n")
            self.assertEqual((dest / "b.txt").read_text(encoding="utf-8"), "beta\n")
            mode = (dest / "sub" / "run.sh").stat().st_mode
            self.assertTrue(bool(mode & stat.S_IXUSR))

    def test_unpack_rejects_traversal_abs_and_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "dest"

            def add_abs(tf):
                info = tarfile.TarInfo("/etc/evil")
                data = b"x"
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))

            def add_dotdot(tf):
                info = tarfile.TarInfo("sub/../../escape.txt")
                data = b"x"
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))

            def add_symlink(tf):
                info = tarfile.TarInfo("link")
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                tf.addfile(info)

            def add_hardlink(tf):
                info = tarfile.TarInfo("hlink")
                info.type = tarfile.LNKTYPE
                info.linkname = "target"
                tf.addfile(info)

            def add_chrdev(tf):
                info = tarfile.TarInfo("devnode")
                info.type = tarfile.CHRTYPE
                tf.addfile(info)

            for builder in (add_abs, add_dotdot, add_symlink, add_hardlink, add_chrdev):
                bad_tar = _make_tar_gz_bytes(builder)
                with self.assertRaises(CryptoError):
                    unpack_bytes(bad_tar, dest)


if __name__ == "__main__":
    unittest.main()
