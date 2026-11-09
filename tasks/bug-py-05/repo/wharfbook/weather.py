"""风浪禁航窗口。禁航本身用潮汐模块折叠，不进巷道账本。"""

from typing import List, Sequence, Tuple

from tidebook.span import cut_minutes, fold_minutes

Span = Tuple[int, int]

# 蒲氏风级 -> 是否停止靠泊
STOP_FROM_BEAUFORT = 7


def stopped(beaufort: int) -> bool:
    if type(beaufort) is not int or beaufort < 0 or beaufort > 12:
        raise ValueError("风级不合法")
    return beaufort >= STOP_FROM_BEAUFORT


def closures_from(samples: Sequence[Tuple[int, int]]) -> List[Span]:
    """samples 是 (分钟, 风级)，按时间升序。连续停航收成半开区间。"""
    if not samples:
        return []
    spans: List[Span] = []
    open_at = None
    previous = None
    for minute, beaufort in samples:
        if previous is not None and minute < previous:
            raise ValueError("风级样本必须按时间升序")
        previous = minute
        if stopped(beaufort):
            if open_at is None:
                open_at = minute
        elif open_at is not None:
            spans.append((open_at, minute))
            open_at = None
    if open_at is not None and samples:
        spans.append((open_at, samples[-1][0] + 1))
    return fold_minutes(spans)


def navigable(windows: Sequence[Span], samples: Sequence[Tuple[int, int]]) -> List[Span]:
    return cut_minutes(windows, closures_from(samples))
