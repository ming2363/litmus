"""货类衔接。洗舱间隔只在配载顺序里使用。"""

from typing import Dict, List, Optional, Sequence, Tuple

# 洗舱分钟。键是 (前货, 后货)。没有键表示不能衔接。
PURGE_MINUTES: Dict[Tuple[str, str], int] = {
    ("干散", "干散"): 0,
    ("干散", "件杂"): 20,
    ("干散", "冷藏"): 40,
    ("件杂", "件杂"): 0,
    ("件杂", "干散"): 15,
    ("件杂", "冷藏"): 30,
    ("冷藏", "冷藏"): 0,
    ("冷藏", "件杂"): 25,
    ("冷藏", "干散"): 45,
    ("化工", "化工"): 10,
}

CLASSES = ("干散", "件杂", "冷藏", "化工")


def purge_gap(previous: str, following: str) -> Optional[int]:
    """能衔接时返回需要空出的分钟，不能衔接时返回 None。"""
    if previous not in CLASSES or following not in CLASSES:
        raise ValueError("未知货类")
    return PURGE_MINUTES.get((previous, following))


def can_follow(previous: str, following: str) -> bool:
    return purge_gap(previous, following) is not None


def sequence_gaps(classes: Sequence[str]) -> List[int]:
    """相邻货类的洗舱分钟。任何一对不能衔接就抛错。"""
    if len(classes) < 2:
        return []
    gaps = []
    for index in range(len(classes) - 1):
        gap = purge_gap(classes[index], classes[index + 1])
        if gap is None:
            raise ValueError("货类不能衔接: {} -> {}".format(classes[index], classes[index + 1]))
        gaps.append(gap)
    return gaps


def total_purge(classes: Sequence[str]) -> int:
    return sum(sequence_gaps(classes))


def reefer_run(classes: Sequence[str]) -> bool:
    return "冷藏" in classes


def compatible_set(anchor: str) -> List[str]:
    return [name for name in CLASSES if can_follow(anchor, name)]
