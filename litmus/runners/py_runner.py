"""Python 隔离测试运行器：以 python3 -I -S -B 启动（不加载第三方包），逐条输出 JSON 行。"""

import argparse
import importlib.util
import json
import os
import signal
import sys
import traceback
import types
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Set


class _CaseTimeout(BaseException):
    """继承 BaseException，防止被被测代码 except Exception 捕获。"""


def _read_lines_set(path_str: Optional[str]) -> Optional[Set[str]]:
    if not path_str:
        return None
    lines = Path(path_str).read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip()}


def _read_timeouts(path_str: Optional[str]) -> Dict[str, float]:
    if not path_str:
        return {}
    raw = json.loads(Path(path_str).read_text(encoding="utf-8"))
    out: Dict[str, float] = {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            out[str(k)] = float(v)
    return out


def _site_dirs() -> List[str]:
    """返回本解释器的第三方包目录（site-packages / dist-packages）。"""
    import site

    dirs: List[str] = []
    try:
        dirs.extend(site.getsitepackages())
    except AttributeError:  # 个别虚拟环境实现没有 getsitepackages
        pass
    return dirs


def _is_site_dir(path: str, site_dirs: List[str]) -> bool:
    if not path:
        return False
    real = os.path.realpath(path)
    if real in {os.path.realpath(d) for d in site_dirs}:
        return True
    parts = real.split(os.sep)
    return "site-packages" in parts or "dist-packages" in parts


def project_path_order(paths: List[str], project: str, site_dirs: List[str]) -> List[str]:
    """把项目目录插到第一个第三方包目录之前；没有第三方包目录时追加到末尾。"""
    result = [p for p in paths if os.path.realpath(p or ".") != os.path.realpath(project)]
    for i, p in enumerate(result):
        if _is_site_dir(p, site_dirs):
            return result[:i] + [project] + result[i:]
    return result + [project]


def _ensure_pkg_chain(mod_parts: List[str], project_root: Path) -> None:
    """当测试目录缺少 __init__.py 时，为模块父路径创建包占位，保证用例 ID 为 模块.类.方法。"""
    for i in range(1, len(mod_parts)):
        pkg_name = ".".join(mod_parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [str(project_root.joinpath(*mod_parts[:i]))]
            sys.modules[pkg_name] = pkg


def _discover_suite(project_dir: Path) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    discovered_files: Set[Path] = set()

    # 优先使用标准 discover 扫描含 __init__.py 的包与根目录测试
    base_suite = loader.discover(
        start_dir=str(project_dir),
        top_level_dir=str(project_dir),
        pattern="test*.py",
    )
    suite.addTests(base_suite)

    # 记录已被 discover 加载的文件，避免重复导入
    ignore_dirs = {"out", "build", "target", "__pycache__", ".pytest_cache", ".git"}
    for mod in list(sys.modules.values()):
        mfile = getattr(mod, "__file__", None)
        if mfile:
            try:
                discovered_files.add(Path(mfile).resolve())
            except OSError:
                pass

    # 补充扫描位于无 __init__.py 子目录下的 test*.py
    for dirpath, dirnames, filenames in os.walk(str(project_dir), followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in ignore_dirs)
        cur = Path(dirpath)
        for fname in sorted(filenames):
            if not (fname.startswith("test") and fname.endswith(".py")):
                continue
            fpath = (cur / fname).resolve()
            if fpath in discovered_files:
                continue
            rel = fpath.relative_to(project_dir.resolve())
            parts = list(rel.with_suffix("").parts)
            mod_name = ".".join(parts)
            _ensure_pkg_chain(parts, project_dir.resolve())
            spec = importlib.util.spec_from_file_location(mod_name, str(fpath))
            if spec is not None and spec.loader is not None:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
                suite.addTests(loader.loadTestsFromModule(mod))
                discovered_files.add(fpath)
    return suite


def _filter_suite(suite: unittest.TestSuite, allowed_ids: Optional[Set[str]]) -> unittest.TestSuite:
    if allowed_ids is None:
        return suite
    filtered = unittest.TestSuite()
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            sub = _filter_suite(item, allowed_ids)
            if sub.countTestCases() > 0:
                filtered.addTest(sub)
        else:
            if item.id() in allowed_ids:
                filtered.addTest(item)
    return filtered


class _JsonLineResult(unittest.TestResult):
    def __init__(self, real_out, timeouts: Dict[str, float]) -> None:
        super().__init__()
        self.real_out = real_out
        self.timeouts = timeouts
        self._old_handler = None
        self._emitted: Set[str] = set()

    def _emit(self, test_id: str, status: str, message: str) -> None:
        if test_id in self._emitted:
            return
        self._emitted.add(test_id)
        line = json.dumps(
            {"id": test_id, "status": status, "message": message},
            ensure_ascii=False,
        )
        self.real_out.write(line + "\n")
        self.real_out.flush()

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        tid = test.id()
        timeout_s = self.timeouts.get(tid)
        if timeout_s is not None and timeout_s > 0:
            def _on_alarm(signum, frame) -> None:
                raise _CaseTimeout("用例超时 ({}s)".format(timeout_s))

            self._old_handler = signal.signal(signal.SIGALRM, _on_alarm)
            signal.setitimer(signal.ITIMER_REAL, timeout_s)
        else:
            self._old_handler = None

    def stopTest(self, test: unittest.TestCase) -> None:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        if self._old_handler is not None:
            signal.signal(signal.SIGALRM, self._old_handler)
            self._old_handler = None
        super().stopTest(test)

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self._emit(test.id(), "pass", "")

    def addFailure(self, test: unittest.TestCase, err) -> None:
        super().addFailure(test, err)
        msg = "".join(traceback.format_exception(*err)).strip()
        self._emit(test.id(), "fail", msg[-1000:])

    def addError(self, test: unittest.TestCase, err) -> None:
        super().addError(test, err)
        if err[0] is not None and issubclass(err[0], _CaseTimeout):
            self._emit(test.id(), "timeout", str(err[1]))
        else:
            msg = "".join(traceback.format_exception(*err)).strip()
            self._emit(test.id(), "error", msg[-1000:])

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self._emit(test.id(), "fail", "skipped: {}".format(reason))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--tests-file", default=None)
    parser.add_argument("--timeouts-file", default=None)
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    allowed_ids = _read_lines_set(args.tests_file)
    timeouts = _read_timeouts(args.timeouts_file)

    # 先保存真实 stdout 再重定向，确保业务代码的 print 不破坏 JSON 行输出
    real_out = sys.stdout
    sys.stdout = sys.stderr

    # 项目路径放在标准库之后、第三方包目录之前：既不遮蔽标准库，
    # 也不让本机已安装的同名第三方包（如 markdown）遮蔽题目仓库里的包
    sys.path[:] = project_path_order(sys.path, str(project_dir), _site_dirs())

    suite = _discover_suite(project_dir)
    suite = _filter_suite(suite, allowed_ids)
    result = _JsonLineResult(real_out, timeouts)
    suite.run(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
