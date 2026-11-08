#!/usr/bin/env python3
"""litmus 出题管理命令行入口。"""

import argparse
import sys
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="author.py",
        description="litmus 出题管理与校验工具",
    )
    parser.add_argument("--version", action="version", version="author 0.1.0")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
