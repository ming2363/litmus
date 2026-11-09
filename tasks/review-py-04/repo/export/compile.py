"""按巷道生成抄表查询。"""

import logging

from export.filters import pattern_ok

logger = logging.getLogger("export.compile")


def statements_for(lane: str) -> str:
    if not pattern_ok(lane):
        raise ValueError("巷道编号不合法")
    logger.info("compile lane=%s", lane)
    return "SELECT id, energy, taken_at FROM readings WHERE lane = '{}'".format(lane)
