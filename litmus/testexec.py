"""在指定目录中编译并调用内置运行器执行 Python / Java 单元测试。"""

import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from litmus.paths import is_ignored_relpath, runners_dir


class CompileError(Exception):
    """编译或语法校验失败。"""


class TestTimeoutError(Exception):
    """测试执行超过整体超时时间。"""


@dataclass(frozen=True)
class TestOutcome:
    id: str
    status: str  # "pass" | "fail" | "error" | "timeout"
    message: str


def _collect_source_files(project_dir: Path, suffix: str) -> List[Path]:
    root = Path(project_dir)
    found: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        cur = Path(dirpath)
        kept: List[str] = []
        for dname in sorted(dirnames):
            rel_dir = (cur / dname).relative_to(root).as_posix() + "/x"
            if not is_ignored_relpath(rel_dir):
                kept.append(dname)
        dirnames[:] = kept
        for fname in sorted(filenames):
            if not fname.endswith(suffix):
                continue
            fpath = cur / fname
            rel = fpath.relative_to(root).as_posix()
            if not is_ignored_relpath(rel):
                found.append(fpath)
    return found


def _compile_python(project_dir: Path) -> None:
    py_files = _collect_source_files(project_dir, ".py")
    if not py_files:
        raise CompileError("未找到任何 Python 源文件")
    for py_file in py_files:
        # 不能把字节码写到 os.devnull：它不是普通文件，py_compile 会直接抛 FileExistsError。
        fd, cfile = tempfile.mkstemp(prefix="litmus_pyc_", suffix=".pyc")
        os.close(fd)
        try:
            try:
                py_compile.compile(str(py_file), cfile=cfile, doraise=True)
            except py_compile.PyCompileError as exc:
                raise CompileError("Python 语法检查失败 ({}): {}".format(py_file.name, exc.msg))
        finally:
            try:
                os.remove(cfile)
            except OSError:
                pass


def _collect_java_project_files(project_dir: Path) -> List[Path]:
    files = _collect_source_files(project_dir, ".java")
    # 排除工作目录中可能伪造的 JavaRunner.java
    filtered: List[Path] = []
    for f in files:
        rel = f.relative_to(project_dir).as_posix()
        if f.name == "JavaRunner.java" or rel == "litmus/runner/JavaRunner.java":
            continue
        filtered.append(f)
    return filtered


def _compile_java_into(project_dir: Path, out_dir: Path) -> None:
    java_files = _collect_java_project_files(project_dir)
    if not java_files:
        raise CompileError("未找到任何 Java 源文件")
    if out_dir.exists():
        shutil.rmtree(str(out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["javac", "-encoding", "UTF-8", "-d", str(out_dir)] + [str(p) for p in java_files]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        err_msg = (proc.stderr or proc.stdout).strip()
        raise CompileError("javac 编译失败:\n{}".format(err_msg))


def compile_project(lang: str, project_dir: Path) -> None:
    """仅执行编译检查，用于可合入性检查阶段。"""
    proj = Path(project_dir)
    if lang == "python":
        _compile_python(proj)
    elif lang == "java":
        _compile_java_into(proj, proj / "out")
    else:
        raise ValueError("不支持的测试语言: {}".format(lang))


def _parse_json_lines(stdout_text: str) -> Dict[str, TestOutcome]:
    outcomes: Dict[str, TestOutcome] = {}
    for raw_line in stdout_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or "id" not in obj or "status" not in obj:
            continue
        tid = str(obj["id"])
        outcomes[tid] = TestOutcome(
            id=tid,
            status=str(obj["status"]),
            message=str(obj.get("message", "")),
        )
    return outcomes


def run_tests(
    lang: str,
    project_dir: Path,
    test_ids: Optional[Sequence[str]] = None,
    timeouts: Optional[Dict[str, float]] = None,
    overall_timeout: float = 120.0,
) -> Dict[str, TestOutcome]:
    """在项目目录编译并运行测试，返回按用例 ID 索引的 TestOutcome 字典。"""
    proj = Path(project_dir).resolve()
    timeouts = dict(timeouts or {})

    with tempfile.TemporaryDirectory(prefix="litmus_run_") as tmp_dir:
        tmp = Path(tmp_dir)
        tests_file: Optional[Path] = None
        if test_ids is not None:
            tests_file = tmp / "tests.txt"
            tests_file.write_bytes(("\n".join(test_ids) + "\n").encode("utf-8"))

        if lang == "python":
            _compile_python(proj)
            timeouts_file = tmp / "timeouts.json"
            timeouts_file.write_bytes((json.dumps(timeouts, ensure_ascii=False)).encode("utf-8"))
            runner_script = runners_dir() / "py_runner.py"
            cmd: List[str] = [
                sys.executable,
                "-I",
                # 不加载 site-packages：题目只允许标准库，本机装没装第三方包（如 Pygments、PyYAML）
                # 都不能改变判分结果，也不能让已安装的同名包遮蔽题目仓库
                "-S",
                "-B",
                str(runner_script),
                "--project",
                str(proj),
                "--timeouts-file",
                str(timeouts_file),
            ]
            if tests_file is not None:
                cmd.extend(["--tests-file", str(tests_file)])

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(proj),
                    capture_output=True,
                    text=True,
                    timeout=overall_timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                raise TestTimeoutError("Python 测试整体运行超时 ({}s)".format(overall_timeout))

            if proc.returncode != 0 and not proc.stdout.strip():
                raise CompileError("Python 运行器异常退出 ({}): {}".format(proc.returncode, proc.stderr.strip()))
            return _parse_json_lines(proc.stdout)

        if lang == "java":
            out_dir = proj / "out"
            _compile_java_into(proj, out_dir)

            # 把内置 JavaRunner.java 编译到独立目录，并在 classpath 放在最前面
            runner_out = tmp / "runner_out"
            runner_out.mkdir(parents=True, exist_ok=True)
            runner_java = runners_dir() / "JavaRunner.java"
            r_compile = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(runner_out), str(runner_java)],
                capture_output=True,
                text=True,
                check=False,
            )
            if r_compile.returncode != 0:
                raise CompileError("内置 JavaRunner 编译失败: {}".format(r_compile.stderr.strip()))

            timeouts_tsv = tmp / "timeouts.tsv"
            tsv_lines = ["{}\t{}".format(k, v) for k, v in timeouts.items()]
            timeouts_tsv.write_bytes(("\n".join(tsv_lines) + "\n").encode("utf-8"))

            classpath = "{}{}{}".format(runner_out, os.pathsep, out_dir)
            cmd = [
                "java",
                "-cp",
                classpath,
                "litmus.runner.JavaRunner",
                "--classes",
                str(out_dir),
                "--timeouts-file",
                str(timeouts_tsv),
            ]
            if tests_file is not None:
                cmd.extend(["--tests-file", str(tests_file)])

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(proj),
                    capture_output=True,
                    text=True,
                    timeout=overall_timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                raise TestTimeoutError("Java 测试整体运行超时 ({}s)".format(overall_timeout))

            if proc.returncode != 0 and not proc.stdout.strip():
                raise CompileError("Java 运行器异常退出 ({}): {}".format(proc.returncode, proc.stderr.strip()))
            return _parse_json_lines(proc.stdout)

        raise ValueError("不支持的测试语言: {}".format(lang))
