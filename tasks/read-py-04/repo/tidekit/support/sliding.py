"""滑动窗口最值，窗口按到达顺序。"""

import collections as _collections


def window_max(values, width):
    """每个位置给出以它结尾的宽度内最大值。宽度不足时用已有元素。"""
    if width <= 0:
        raise ValueError("width")
    dq = _collections.deque()
    out = []
    for idx, value in enumerate(values):
        while dq and dq[0] <= idx - width:
            dq.popleft()
        while dq and values[dq[-1]] <= value:
            dq.pop()
        dq.append(idx)
        out.append(values[dq[0]])
    return out


def window_sum(values, width):
    """同窗口的和。"""
    if width <= 0:
        raise ValueError("width")
    out = []
    running = 0
    for idx, value in enumerate(values):
        running += value
        if idx >= width:
            running -= values[idx - width]
        out.append(running)
    return out
