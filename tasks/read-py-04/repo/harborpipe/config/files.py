"""从旁路文件读取家族表。"""

import json
from pathlib import Path
from typing import Dict


def load_overlay(path: Path) -> Dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("家族表必须是对象")
    return {str(key): str(value) for key, value in raw.items()}


def family_from_file(path: Path, operation: str) -> str:
    table = load_overlay(path)
    if operation in table:
        return table[operation]
    prefix = operation.rsplit(".", 1)[0]
    if prefix in table:
        return table[prefix]
    raise KeyError(operation)
