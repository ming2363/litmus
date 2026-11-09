"""箱务备注。和调用链无关，给现场交接看。"""

from typing import Dict, List, Tuple

Note = Tuple[int, str, str]


class NoteBook:
    def __init__(self) -> None:
        self._rows: Dict[str, List[Note]] = {}

    def add(self, box_id: str, minute: int, author: str, text: str) -> None:
        if not box_id or not author or not text:
            raise ValueError("备注不完整")
        if type(minute) is not int:
            raise ValueError("分钟必须是整数")
        bucket = self._rows.setdefault(box_id, [])
        if bucket and minute < bucket[-1][0]:
            raise ValueError("备注时间倒退")
        bucket.append((minute, author, text))

    def of(self, box_id: str) -> List[Note]:
        return list(self._rows.get(box_id, []))

    def authors(self, box_id: str) -> List[str]:
        return sorted({author for _minute, author, _text in self.of(box_id)})

    def search(self, word: str) -> List[Tuple[str, Note]]:
        if not word:
            raise ValueError("关键词为空")
        found = []
        for box_id, rows in self._rows.items():
            for note in rows:
                if word in note[2]:
                    found.append((box_id, note))
        found.sort(key=lambda item: (item[1][0], item[0]))
        return found

    def latest(self, box_id: str) -> Note:
        rows = self.of(box_id)
        if not rows:
            raise KeyError(box_id)
        return rows[-1]

    def between(self, start: int, end: int) -> List[Tuple[str, Note]]:
        if start >= end:
            raise ValueError("区间不合法")
        rows = []
        for box_id, notes in self._rows.items():
            for note in notes:
                if start <= note[0] < end:
                    rows.append((box_id, note))
        rows.sort(key=lambda item: (item[1][0], item[0]))
        return rows
