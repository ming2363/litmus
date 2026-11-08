#!/usr/bin/env python3
"""litmus 做题命令行入口。"""

import sys
from typing import List, Optional

from litmus.cli_player import main as _player_main


def main(argv: Optional[List[str]] = None) -> int:
    return _player_main(argv)


if __name__ == "__main__":
    sys.exit(main())
