"""编辑距离，给编码纠错提示用。"""


def distance(left, right):
    """经典动态规划，插入、删除、替换代价都是 1。"""
    if left is None or right is None:
        raise TypeError("text")
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    prev = list(range(len(right) + 1))
    for i, ch_l in enumerate(left, start=1):
        curr = [i]
        for j, ch_r in enumerate(right, start=1):
            cost = 0 if ch_l == ch_r else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def closest(query, choices, max_distance):
    """返回距离不超过阈值的候选项，按距离再按字典序。"""
    found = []
    for item in choices:
        dist = distance(query, item)
        if dist <= max_distance:
            found.append((dist, item))
    found.sort()
    return [item for _dist, item in found]
