#!/usr/bin/env python3
"""litmus 做题命令行入口。"""

import argparse
import sys
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="litmus.py",
        description="litmus 编程能力测评做题工具",
    )
    parser.add_argument("--version", action="version", version="litmus 0.1.0")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
