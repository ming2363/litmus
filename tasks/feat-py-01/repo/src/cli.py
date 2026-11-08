"""记账命令行入口。"""

import argparse
from pathlib import Path
import sys
from typing import Optional, Sequence, TextIO

from src.ledger import (
    filter_entries,
    format_list_output,
    format_summary_output,
    summarize_entries,
)
from src.storage import load_entries


class _NoExitParser(argparse.ArgumentParser):
    """解析失败时通过抛异常交由 main 返回非零状态码。"""

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValueError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = _NoExitParser(prog="ledger", description="个人收支记账工具")
    sub = parser.add_subparsers(dest="command")

    for name in ("list", "summary"):
        p = sub.add_parser(name)
        p.add_argument("--file", required=True, help="CSV 账目文件路径")
        p.add_argument("--category", default=None, help="按分类名称过滤")
    return parser


def main(
    argv: Optional[Sequence[str]] = None,
    stdout: Optional[TextIO] = None,
    stderr: Optional[TextIO] = None,
) -> int:
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except ValueError as exc:
        err.write("参数错误: {}\n".format(exc))
        return 2

    if args.command not in ("list", "summary"):
        err.write("请指定子命令: list 或 summary\n")
        return 2

    try:
        entries = load_entries(Path(args.file))
    except (OSError, ValueError) as exc:
        err.write("读取账目失败: {}\n".format(exc))
        return 1

    filtered = filter_entries(entries, category=args.category)
    if args.command == "list":
        out.write(format_list_output(filtered))
    else:
        summary = summarize_entries(filtered)
        out.write(format_summary_output(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
