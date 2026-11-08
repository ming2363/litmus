"""标准库加密打包工具：tar.gz + HMAC-SHA256 CTR 加密 + HMAC-SHA256 认证。"""

import gzip
import hashlib
import hmac
import io
import os
import stat
import tarfile
import tempfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Tuple

MAGIC: bytes = b"LITMUS1"
NONCE_SIZE = 16
TAG_SIZE = 32
MASTER_KEY: bytes = b"litmus-v1-master-key-2026-engine"


class CryptoError(Exception):
    """加解密或安全解包失败。"""


def _derive_keys() -> Tuple[bytes, bytes]:
    k_enc = hmac.new(MASTER_KEY, b"litmus-enc", hashlib.sha256).digest()
    k_mac = hmac.new(MASTER_KEY, b"litmus-mac", hashlib.sha256).digest()
    return k_enc, k_mac


def _xor_keystream(k_enc: bytes, nonce: bytes, data: bytes) -> bytes:
    """使用 HMAC-SHA256(k_enc, nonce + counter_be64) 生成密钥流并逐块异或。"""
    if not data:
        return b""
    out = bytearray()
    total = len(data)
    offset = 0
    counter = 0
    while offset < total:
        block = hmac.new(
            k_enc, nonce + counter.to_bytes(8, "big"), hashlib.sha256
        ).digest()
        chunk = data[offset : offset + 32]
        out.extend(a ^ b for a, b in zip(chunk, block))
        offset += 32
        counter += 1
    return bytes(out)


def encrypt(data: bytes) -> bytes:
    """先加密后认证（Encrypt-then-MAC）：LITMUS1 + nonce(16) + ct + tag(32)。"""
    k_enc, k_mac = _derive_keys()
    nonce = os.urandom(NONCE_SIZE)
    ct = _xor_keystream(k_enc, nonce, data)
    header_and_ct = MAGIC + nonce + ct
    tag = hmac.new(k_mac, header_and_ct, hashlib.sha256).digest()
    return header_and_ct + tag


def decrypt(blob: bytes) -> bytes:
    """先用恒定时间比较校验 tag，再解密密文。"""
    min_len = len(MAGIC) + NONCE_SIZE + TAG_SIZE
    if len(blob) < min_len:
        raise CryptoError("密文长度不合法")
    if blob[: len(MAGIC)] != MAGIC:
        raise CryptoError("密文格式标识不匹配")

    nonce_start = len(MAGIC)
    nonce_end = nonce_start + NONCE_SIZE
    nonce = blob[nonce_start:nonce_end]
    ct = blob[nonce_end:-TAG_SIZE]
    tag = blob[-TAG_SIZE:]

    k_enc, k_mac = _derive_keys()
    expected_tag = hmac.new(k_mac, MAGIC + nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise CryptoError("密文完整性校验失败")

    return _xor_keystream(k_enc, nonce, ct)


def pack_dir(path: Path) -> bytes:
    """将目录打包为可复现的 tar.gz 字节流（排序成员、清零 mtime/uid/gid）。"""
    src = Path(path)
    if not src.is_dir():
        raise CryptoError("待打包路径不是目录: {}".format(src))

    entries = []
    for root_str, dirnames, filenames in os.walk(str(src), followlinks=False):
        root_path = Path(root_str)
        # 检查目录自身是否为符号链接
        dirnames.sort()
        filenames.sort()
        for dname in dirnames:
            dpath = root_path / dname
            if dpath.is_symlink():
                raise CryptoError("禁止打包符号链接目录: {}".format(dpath))
            rel = dpath.relative_to(src).as_posix()
            entries.append((rel, dpath, True))
        for fname in filenames:
            fpath = root_path / fname
            if fpath.is_symlink():
                raise CryptoError("禁止打包符号链接文件: {}".format(fpath))
            rel = fpath.relative_to(src).as_posix()
            entries.append((rel, fpath, False))

    entries.sort(key=lambda item: item[0])

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tf:
            for rel, item_path, is_dir in entries:
                info = tarfile.TarInfo(name=rel)
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                if is_dir:
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    tf.addfile(info)
                else:
                    raw = item_path.read_bytes()
                    st_mode = item_path.stat().st_mode
                    info.type = tarfile.REGTYPE
                    info.mode = 0o755 if (st_mode & stat.S_IXUSR) else 0o644
                    info.size = len(raw)
                    tf.addfile(info, io.BytesIO(raw))
    return buf.getvalue()


def _validate_member_path(name: str, dest_resolved: Path) -> Path:
    if not name or name.startswith("/") or "\\" in name:
        raise CryptoError("非法归档路径: {}".format(name))
    # 兼容 Windows 盘符前缀检查
    if len(name) >= 2 and name[1] == ":":
        raise CryptoError("非法归档路径: {}".format(name))
    posix = PurePosixPath(name)
    if posix.is_absolute():
        raise CryptoError("禁止绝对路径成员: {}".format(name))
    for part in posix.parts:
        if part == "..":
            raise CryptoError("禁止路径穿越成员: {}".format(name))
    target = (dest_resolved / posix).resolve()
    if target != dest_resolved and dest_resolved not in target.parents:
        raise CryptoError("解包目标越界: {}".format(name))
    return target


def unpack_bytes(data: bytes, dest: Path) -> None:
    """安全校验后解包 tar.gz 到目标目录，不依赖 Python 版本相关的 tarfile filter。"""
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    dest_resolved = dest_path.resolve()

    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            members = tf.getmembers()
            validated = []
            for member in members:
                if member.issym() or member.islnk():
                    raise CryptoError("禁止链接成员: {}".format(member.name))
                if not (member.isreg() or member.isdir()):
                    raise CryptoError("禁止特殊文件成员: {}".format(member.name))
                if member.name in (".", "./"):
                    continue
                target = _validate_member_path(member.name, dest_resolved)
                validated.append((member, target))

            for member, target in validated:
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    src_f = tf.extractfile(member)
                    if src_f is None:
                        raise CryptoError("无法读取归档成员: {}".format(member.name))
                    content = src_f.read()
                    target.write_bytes(content)
                    mode = 0o755 if (member.mode & 0o111) else 0o644
                    os.chmod(str(target), mode)
    except (tarfile.TarError, EOFError, zlib.error, OSError) as exc:
        if isinstance(exc, CryptoError):
            raise
        raise CryptoError("归档解析或解包失败: {}".format(exc))


def seal_dir(src: Path, out_file: Path) -> None:
    """打包并加密目录，原子写出到目标密文文件。"""
    packed = pack_dir(src)
    blob = encrypt(packed)
    out = Path(out_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(out.parent),
            prefix=".tmp_seal_",
            suffix=".enc",
            delete=False,
        ) as f:
            tmp_path = Path(f.name)
            f.write(blob)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp_path), str(out))
        tmp_path = None
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def unseal_to(enc_file: Path, dest: Path) -> None:
    """读取密文文件、解密并安全解包到目标目录。"""
    enc_path = Path(enc_file)
    if not enc_path.is_file():
        raise CryptoError("密文文件不存在: {}".format(enc_path))
    blob = enc_path.read_bytes()
    packed = decrypt(blob)
    unpack_bytes(packed, dest)
