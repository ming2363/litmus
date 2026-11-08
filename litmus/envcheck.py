"""start 的 7 项环境与防作弊检查（对应设计文档 4.2）。"""

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from litmus.crypto import CryptoError, unseal_to
from litmus.integrity import (
    find_forbidden_files,
    get_dirty_paths,
    get_git_head,
    is_git_repo,
)
from litmus.paths import answers_dir, grade_root_dir, runs_dir
from litmus.tasks import TaskValidationError, load_manifest


@dataclass(frozen=True)
class CheckItem:
    name: str
    passed: bool
    detail: str
    fix_hint: str = ""


@dataclass(frozen=True)
class EnvCheckResult:
    ok: bool
    items: List[CheckItem]
    env_info: Dict[str, str]


def _default_run_cmd(cmd: Sequence[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _parse_java_major(output: str) -> Optional[int]:
    m = re.search(r'"(\d+)(?:\.(\d+))?', output)
    if not m:
        m = re.search(r'\bjavac\s+(\d+)(?:\.(\d+))?', output)
    if not m:
        return None
    major = int(m.group(1))
    if major == 1 and m.group(2):
        return int(m.group(2))
    return major


def check_toolchains(
    python_version_info: Optional[Tuple[int, int, int]] = None,
    which_fn: Optional[Callable[[str], Optional[str]]] = None,
    run_cmd_fn: Optional[Callable[[Sequence[str]], Tuple[int, str, str]]] = None,
) -> Tuple[CheckItem, Dict[str, str]]:
    """检查 1：Python >= 3.9，java 与 javac 都存在且版本 >= 17，git 存在。"""
    py_ver = python_version_info or (
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    which = which_fn or shutil.which
    run_cmd = run_cmd_fn or _default_run_cmd
    env_info: Dict[str, str] = {
        "python_version": "{}.{}.{}".format(py_ver[0], py_ver[1], py_ver[2]),
        "java_version": "unknown",
        "javac_version": "unknown",
        "git_version": "unknown",
    }
    errors: List[str] = []

    if py_ver < (3, 9, 0):
        errors.append("Python 版本需 >= 3.9，当前为 {}".format(env_info["python_version"]))

    if not which("git"):
        errors.append("未找到 git 命令")
    else:
        rc, out, err = run_cmd(["git", "--version"])
        if rc != 0:
            errors.append("git --version 执行失败")
        else:
            env_info["git_version"] = (out or err).strip()

    if not which("java"):
        errors.append("未找到 java 命令")
    else:
        rc, out, err = run_cmd(["java", "-version"])
        text = (err or out).strip()
        major = _parse_java_major(text)
        env_info["java_version"] = text.splitlines()[0] if text else "unknown"
        if rc != 0 or major is None or major < 17:
            errors.append("java 版本需 >= 17，当前为: {}".format(env_info["java_version"]))

    if not which("javac"):
        errors.append("未找到 javac（仅 JRE 不满足要求）")
    else:
        rc, out, err = run_cmd(["javac", "-version"])
        text = (out or err).strip()
        major = _parse_java_major(text)
        env_info["javac_version"] = text.splitlines()[0] if text else "unknown"
        if rc != 0 or major is None or major < 17:
            errors.append("javac 版本需 >= 17，当前为: {}".format(env_info["javac_version"]))

    if errors:
        return (
            CheckItem(
                name="工具链版本检查",
                passed=False,
                detail="；".join(errors),
                fix_hint="请安装 Python 3.9+、JDK 17+（含 javac）和 Git 并确保在 PATH 中可用",
            ),
            env_info,
        )
    return CheckItem(name="工具链版本检查", passed=True, detail="Python / JDK / Git 就绪"), env_info


def check_git_clean(root: Optional[Path] = None) -> CheckItem:
    """检查 2：当前目录为 git 仓库且受保护路径无未提交改动。"""
    if not is_git_repo(root) or get_git_head(root) is None:
        return CheckItem(
            name="Git 仓库干净度检查",
            passed=False,
            detail="当前目录不是有效 git 仓库或尚无提交记录",
            fix_hint="请在已完成初始提交的 litmus git 仓库根目录执行",
        )
    dirty = get_dirty_paths(
        paths=("litmus.py", "litmus", "tasks", "answers"),
        include_untracked=True,
        root=root,
    )
    if dirty:
        return CheckItem(
            name="Git 仓库干净度检查",
            passed=False,
            detail="存在未提交改动: {}".format("; ".join(dirty)),
            fix_hint="请先提交或清理 litmus.py、litmus/、tasks/、answers/ 下的未提交改动",
        )
    return CheckItem(name="Git 仓库干净度检查", passed=True, detail="受保护路径无未提交改动")


def check_answers_sealed(root: Optional[Path] = None) -> CheckItem:
    """检查 3：answers/ 下没有明文目录，且题库均已有对应 .grade.enc。"""
    adir = answers_dir(root)
    if not adir.is_dir():
        return CheckItem(
            name="答案加密状态检查",
            passed=False,
            detail="answers/ 目录不存在",
            fix_hint="请确认 answers/ 目录存在并已完成题目封包",
        )
    plain_dirs = sorted(p.name for p in adir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if plain_dirs:
        return CheckItem(
            name="答案加密状态检查",
            passed=False,
            detail="answers/ 下存在未清理的明文目录: {}".format(", ".join(plain_dirs)),
            fix_hint="请先执行 seal 完成加密并移除 answers/ 下的明文目录",
        )
    try:
        manifest = load_manifest(root)
    except TaskValidationError as exc:
        return CheckItem(
            name="答案加密状态检查",
            passed=False,
            detail="题目清单校验失败: {}".format(exc),
            fix_hint="请检查 tasks/manifest.json 配置",
        )
    missing_enc = [
        tid for tid in manifest.order if not (adir / "{}.grade.enc".format(tid)).is_file()
    ]
    if missing_enc:
        return CheckItem(
            name="答案加密状态检查",
            passed=False,
            detail="缺少判分密文文件: {}".format(", ".join(missing_enc)),
            fix_hint="请对缺失题号完成加密封包后再开始测评",
        )
    return CheckItem(name="答案加密状态检查", passed=True, detail="全部题目答案均已加密")


def check_no_forbidden_files(root: Optional[Path] = None) -> CheckItem:
    """检查 4：仓库任何位置禁止存在 AGENTS.md / CLAUDE.md / GEMINI.md。"""
    found = find_forbidden_files(root)
    if found:
        return CheckItem(
            name="禁止指令文件检查",
            passed=False,
            detail="发现禁止文件: {}".format(", ".join(found)),
            fix_hint="请删除上述文件并提交干净后再开始测评",
        )
    return CheckItem(name="禁止指令文件检查", passed=True, detail="未发现禁止文件")


def check_crypto_verify(root: Optional[Path] = None) -> CheckItem:
    """检查 5：用内置密钥试解一题 .grade.enc，确认加解密正常。"""
    adir = answers_dir(root)
    enc_files = sorted(adir.glob("*.grade.enc")) if adir.is_dir() else []
    if not enc_files:
        return CheckItem(
            name="加解密自检",
            passed=False,
            detail="answers/ 下没有可验证的 .grade.enc 文件",
            fix_hint="请先对题库完成加密封包",
        )
    target = enc_files[0]
    try:
        with tempfile.TemporaryDirectory(prefix="litmus_crypto_chk_") as tmp:
            unseal_to(target, Path(tmp))
    except CryptoError as exc:
        return CheckItem(
            name="加解密自检",
            passed=False,
            detail="试解 {} 失败: {}".format(target.name, exc),
            fix_hint="请确认密文未被损坏且与当前内置密钥匹配",
        )
    return CheckItem(name="加解密自检", passed=True, detail="验证 {} 解密正常".format(target.name))


def check_ai_relay(mode_file: Optional[Path] = None) -> CheckItem:
    """检查 6：ai-relay 模式必须为 off，或本机未安装 ai-relay。"""
    mpath = mode_file or (Path.home() / ".claude" / "ai-relay" / "mode")
    if not mpath.exists():
        return CheckItem(name="ai-relay 外派检查", passed=True, detail="本机未安装 ai-relay")
    try:
        mode = mpath.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return CheckItem(
            name="ai-relay 外派检查",
            passed=False,
            detail="读取 {} 失败: {}".format(mpath, exc),
            fix_hint="请确认 ai-relay 状态文件可读且内容为 off",
        )
    if mode != "off":
        return CheckItem(
            name="ai-relay 外派检查",
            passed=False,
            detail="当前 ai-relay 模式为 '{}'，测评禁止将任务外派给其他模型".format(mode),
            fix_hint="请先关闭 ai-relay（将 {} 设为 off 或执行关闭命令）".format(mpath),
        )
    return CheckItem(name="ai-relay 外派检查", passed=True, detail="ai-relay 已关闭 (off)")


def check_and_clean_stale_grade_dirs(root: Optional[Path] = None) -> CheckItem:
    """检查 7：清理上次判分异常中断时可能残留的 .grade 临时目录。"""
    rroot = runs_dir(root)
    cleaned = 0
    if rroot.is_dir():
        for entry in sorted(rroot.iterdir()):
            if not entry.is_dir():
                continue
            gdir = grade_root_dir(entry)
            if gdir.exists():
                shutil.rmtree(str(gdir))
                cleaned += 1
    return CheckItem(
        name="残留判分目录清理",
        passed=True,
        detail="已清理 {} 个残留判分目录".format(cleaned),
    )


def run_env_checks(
    root: Optional[Path] = None,
    ai_relay_mode_file: Optional[Path] = None,
) -> EnvCheckResult:
    """执行全部 7 项 start 前置检查。"""
    item1, env_info = check_toolchains()
    items = [
        item1,
        check_git_clean(root),
        check_answers_sealed(root),
        check_no_forbidden_files(root),
        check_crypto_verify(root),
        check_ai_relay(ai_relay_mode_file),
        check_and_clean_stale_grade_dirs(root),
    ]
    return EnvCheckResult(
        ok=all(item.passed for item in items),
        items=items,
        env_info=env_info,
    )
