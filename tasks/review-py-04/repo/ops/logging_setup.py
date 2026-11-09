"""进程日志。"""

import logging
from typing import Optional


def build_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    return logger


def quiet(name: Optional[str] = None) -> None:
    target = logging.getLogger(name) if name else logging.getLogger()
    target.setLevel(logging.WARNING)
