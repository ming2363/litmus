"""把单行访问日志拆成字段。"""

import re
from typing import Dict, List


# 事件名使用贪婪匹配，正文里的同名片段会把边界往后拉。
_LINE = re.compile(
    r"^(?P<date>\S+) (?P<level>DEBUG|INFO|WARN|ERROR) (?P<event>.*) "
    r"duration_ms=(?P<dur>\d+) key=(?P<key>\S+) message=(?P<msg>.*)$"
)


def parse_line(line: str) -> Dict:
    """解析一行。不匹配时抛出 ValueError，消息包含原始行。"""
    if not isinstance(line, str):
        raise ValueError("无法解析: {}".format(line))
    matched = _LINE.match(line)
    if matched is None:
        raise ValueError("无法解析: {}".format(line))
    data = matched.groupdict()
    return {
        "date": data["date"],
        "level": data["level"],
        "event": data["event"],
        "duration_ms": int(data["dur"]),
        "key": data["key"],
        "message": data["msg"],
    }


def parse_lines(text: str) -> List[Dict]:
    """逐行解析，跳过空白行。"""
    if not isinstance(text, str):
        raise ValueError("无法解析: {}".format(text))
    rows = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        rows.append(parse_line(raw))
    return rows
