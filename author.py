#!/usr/bin/env python3
"""litmus 出题管理命令行入口。"""

import sys
from typing import List, Optional

from litmus.cli_author import main as _author_main


def main(argv: Optional[List[str]] = None) -> int:
    return _author_main(argv)


if __name__ == "__main__":
    sys.exit(main())
