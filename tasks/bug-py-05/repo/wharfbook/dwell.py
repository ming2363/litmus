"""在港停留用潮汐模块折叠窗口，不走巷道计划。"""

from typing import List, Sequence, Tuple

from tidebook.span import cut_minutes, fold_minutes

Span = Tuple[int, int]


def billable_spans(spans: Sequence[Span]) -> List[Span]:
    """停留窗口的计费段。"""
    return fold_minutes(spans)


def open_spans(spans: Sequence[Span], closures: Sequence[Span]) -> List[Span]:
    """扣掉封航之后仍可计费的停留。"""
    return cut_minutes(spans, closures)
