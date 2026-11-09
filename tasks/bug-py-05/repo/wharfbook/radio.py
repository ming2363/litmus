"""调度对讲记录。只保留文本，不参与归并。"""

from typing import List, Tuple

Entry = Tuple[int, str, str]


class RadioLog:
    def __init__(self) -> None:
        self._rows: List[Entry] = []

    def speak(self, minute: int, channel: str, text: str) -> None:
        if type(minute) is not int:
            raise ValueError("分钟必须是整数")
        if not channel or not text:
            raise ValueError("频道和内容不能为空")
        self._rows.append((minute, channel.strip().upper(), text.strip()))

    def on(self, channel: str) -> List[Entry]:
        key = channel.strip().upper()
        return [row for row in self._rows if row[1] == key]

    def between(self, start: int, end: int) -> List[Entry]:
        if start >= end:
            raise ValueError("查询区间不合法")
        return [row for row in self._rows if start <= row[0] < end]

    def channels(self) -> List[str]:
        return sorted({row[1] for row in self._rows})

    def last(self, channel: str) -> Entry:
        rows = self.on(channel)
        if not rows:
            raise KeyError(channel)
        return max(rows, key=lambda row: row[0])

    def count(self, channel: str) -> int:
        return len(self.on(channel))

    def transcript(self, channel: str) -> str:
        rows = self.on(channel)
        if not rows:
            return ""
        return "\n".join("{} {}".format(minute, text) for minute, _channel, text in rows)

    def empty(self) -> bool:
        return not self._rows
