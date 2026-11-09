"""把文本行写到导出文件。"""

import logging
from typing import Sequence

logger = logging.getLogger("billing.dump")


def write_dump(path: str, rows: Sequence[str]) -> int:
    handle = open(path, "w", encoding="utf-8")
    logger.info("dump path=%s", path)
    if not rows:
        logger.info("dump empty")
        return 0
    try:
        for row in rows:
            handle.write(row)
            if not row.endswith("\n"):
                handle.write("\n")
        handle.flush()
    finally:
        handle.close()
    return len(rows)
