"""操作名最后一个片段到动词的表。"""

from typing import Callable, List, Tuple

LiveRow = Tuple[int, str, str, int]
LIVE: List[LiveRow] = []


def alias(stem: str, verb: str, priority: int) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def decorate(fn: Callable[..., object]) -> Callable[..., object]:
        LIVE.append((priority, stem, verb, len(LIVE)))
        return fn

    return decorate


class VerbBook:
    def resolve(self, operation: str) -> str:
        stem = operation.rsplit(".", 1)[-1]
        rows = [row for row in LIVE if row[1] == stem]
        if not rows:
            raise KeyError(stem)
        rows.sort(key=lambda row: (-row[0], row[3]))
        return rows[0][2]
